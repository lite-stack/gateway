import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from openstack import connection
from openstack.exceptions import ConflictException, ResourceNotFound, DuplicateResource
from openstack.exceptions import  HttpException as OpenstackHTTPException
from sqlalchemy.ext.asyncio import AsyncSession

import app.openstack.compute_service as openstack
import app.servers.db_service as db
from app.auth.config import fastapi_users
from app.auth.models import User
from app.command.echo import EchoCommand
from app.config import settings
from app.dependencies import get_openstack_connection, get_async_session
from app.command.command import ExecAction
from app.command.grafana import GrafanaCommand
from app.command.matplotlib import MatplotlibCommand
from app.command.mongo import MongoCommand
from app.command.postgres import PostgresCommand
from app.command.pytorch import TorchCommand
from app.command.tensorflow import TensorflowCommand
from app.servers.schemas import (
    Server as ServerSchema,
    ServerDetailed as ServerDetailedSchema,
    ServerStateActionUpdate,
    ServerStateActionEnum, ServerConfiguration, ServeCreate, ServeUpdate, ServerCommand, ServerCommandEnum
)
from app.servers.service import send_keypair_email
from app.openstack.models import get_os_default_user, get_server_public_ip
from app.runner.service import CommandRunner
from fastapi.concurrency import run_in_threadpool

current_user = fastapi_users.current_user()

router = APIRouter(
    prefix="/servers",
    tags=["servers"]
)


@router.get("/configurations", response_model=list[ServerConfiguration])
async def get_server_configurations(
        _: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        server_configurations = await db.get_server_configurations(session)
        server_configurations.sort(key=lambda item: item.name)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server configurations: {e}")

    return server_configurations


@router.get("/limit")
async def get_server_limit(
        conn: connection.Connection = Depends(get_openstack_connection),
        _: User = Depends(current_user),
):
    return {'limit': openstack.get_instance_limit(conn)}


@router.get("", response_model=list[ServerSchema])
async def get_user_servers_list(
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.is_superuser:
            user_servers = await db.get_all_servers(session)
        else:
            user_servers = await db.get_user_servers(user, session)

        if len(user_servers) == 0:
            return []
        server_ids = [server.openstack_id for server in user_servers]
        servers = openstack.get_servers_by_ids(conn, server_ids)

        user_server_map={str(server.openstack_id): server for server in user_servers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server: {e}")

    return [ServerSchema.create_from_openstack_server(user.id, server, user_server_map.get(server.id, {})) for server in servers]


@router.get("/instruments", response_model=list[ServerSchema])
async def get_configurable_user_servers_list(
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.is_superuser:
            user_servers = await db.get_all_servers(session)
        else:
            user_servers = await db.get_user_servers(user, session)

        if len(user_servers) == 0:
            return []

        server_ids = []
        for server in user_servers:
            if 'cirros' not in server.image:
                server_ids.append(server.openstack_id)

        servers = openstack.get_servers_by_ids(conn, server_ids)

        user_server_map={str(server.openstack_id): server for server in user_servers}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server: {e}")

    return [ServerSchema.create_from_openstack_server(user.id, server, user_server_map.get(server.id, {})) for server in servers]

@router.post("/{server_id}/command", status_code=200)
async def run_command_on_server(
        background_tasks: BackgroundTasks,
        server_id: uuid.UUID,
        server_command: ServerCommand,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        if not await db.is_user_server(server_id, user, session):
            return HTTPException(status_code=404, detail="Server not found")

        server = await db.get_user_server(user, str(server_id), session)
        openstack_server = openstack.get_server(conn, str(server_id))
        executor = None
        match server_command.command:
            case ServerCommandEnum.install_torch :
                executor = TorchCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_torch:
                executor = TorchCommand(ExecAction.DELETE)
            case ServerCommandEnum.install_tensorflow:
                executor = TensorflowCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_tensorflow:
                executor = TensorflowCommand(ExecAction.DELETE)
            case ServerCommandEnum.install_grafana:
                executor = GrafanaCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_grafana:
                executor = GrafanaCommand(ExecAction.DELETE)
            case ServerCommandEnum.install_matplotlib:
                executor = MatplotlibCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_matplotlib:
                executor = MatplotlibCommand(ExecAction.DELETE)
            case ServerCommandEnum.install_postgres:
                executor = PostgresCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_postgres:
                executor = PostgresCommand(ExecAction.DELETE)
            case ServerCommandEnum.install_mongo:
                executor = MongoCommand(ExecAction.INSTALL)
            case ServerCommandEnum.delete_mongo:
                executor = MongoCommand(ExecAction.DELETE)
            case ServerCommandEnum.echo:
                executor = EchoCommand()

        if executor:
            background_tasks.add_task(CommandRunner(server, executor, get_server_public_ip(openstack_server)).run)

    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to run command: {e}")

@router.get("/{server_id}", response_model=ServerDetailedSchema)
async def get_user_server(
        server_id: uuid.UUID,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    if not await db.is_user_server(server_id, user, session):
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        image=None
        openstack_server = openstack.get_server(conn, str(server_id))
        if openstack_server.image.id:
            image = openstack.get_image(conn, openstack_server.image.id)
        server = await db.get_user_server(user, str(server_id), session)
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail=f"Server not found")
    except DuplicateResource:
        raise HTTPException(status_code=409, detail=f"Multiple servers found with ID {server_id}")
    except OpenstackHTTPException as e:
        raise HTTPException(status_code=e.status_code, detail=e.details)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server: {e}")

    return ServerDetailedSchema.create_from_openstack_server(user.id,server, openstack_server, image)

@router.get("/{server_id}/console-url")
async def get_user_server_console_url(
        server_id: uuid.UUID,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    if not await db.is_user_server(server_id, user, session):
        raise HTTPException(status_code=404, detail="Server not found")
    try:
        console = openstack.create_server_console(conn, str(server_id))
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail=f"Server not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server console: {e}")

    url = console.get('url', '')
    if url == '':
        raise HTTPException(status_code=500, detail=f"Failed to create server console: no url")

    return {'url': url}

@router.post("/from_configuration", response_model=ServerDetailedSchema)
async def create_user_server(
        background_tasks: BackgroundTasks,
        req: ServeCreate,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        servers = await db.get_user_servers(user, session)
        if len(servers) > openstack.get_instance_limit(conn):
            raise HTTPException(status_code=409, detail="Too many servers")

        server_config = await db.get_server_configuration(req.configuration_name, session)

        openstack_server, key_pair, floating_ip = openstack.create_server(
            conn,
            str(user.id),
            req.name,
            req.description,
            server_config,
        )

        public_ip_address = floating_ip.floating_ip_address
        if key_pair.private_key and settings.mail_username != "" and public_ip_address != "":
            await send_keypair_email(background_tasks, user, key_pair, public_ip_address, get_os_default_user(server_config.image))

        await db.insert_user_server(openstack_server.id, user.id, server_config.image, session)
        server = await db.get_user_server(user, str(openstack_server.id), session)
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=f"Resource not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server: {e}")

    return ServerDetailedSchema.create_from_openstack_server(user.id, server, openstack_server)


@router.delete("/{server_id}", status_code=204)
async def delete_user_server(
        server_id: uuid.UUID,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if not await db.is_user_server(server_id, user, session):
            raise HTTPException(status_code=404, detail="Server not found")

        openstack.delete_server(conn, str(server_id))
        await db.delete_user_server(server_id, session)

    except ResourceNotFound:
        raise HTTPException(status_code=404, detail=f"Server not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server: {e}")

    return


@router.patch("/{server_id}", status_code=200)
async def update_server(
        server_id: uuid.UUID,
        req: ServeUpdate,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if not await db.is_user_server(server_id, user, session):
            raise HTTPException(status_code=404, detail="Server not found")

        openstack.update_server(conn, str(server_id), req.name, req.description)

    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to update server: {e}")


@router.patch("/{server_id}/state", status_code=200)
async def set_state_action(
        server_id: uuid.UUID,
        state_action: ServerStateActionUpdate,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if not await db.is_user_server(server_id, user, session):
            raise HTTPException(status_code=404, detail="Server not found")

        match state_action.action:
            case ServerStateActionEnum.pause:
                openstack.pause_server(conn, str(server_id))
            case ServerStateActionEnum.unpause:
                openstack.unpause_server(conn, str(server_id))
            case ServerStateActionEnum.start:
                openstack.start_server(conn, str(server_id))
            case ServerStateActionEnum.stop:
                openstack.stop_server(conn, str(server_id))
            case ServerStateActionEnum.reboot:
                openstack.reboot_server(conn, str(server_id))
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictException as e:
        raise HTTPException(status_code=409, detail='Invalid status')
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set server state: {e}")
