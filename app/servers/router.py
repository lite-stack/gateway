import uuid

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from openstack import connection
from openstack.exceptions import ConflictException, ResourceNotFound, DuplicateResource
from sqlalchemy.ext.asyncio import AsyncSession

import app.openstack.compute_service as openstack
import app.openstack.network_service as openstack_network
import app.servers.db_service as db
from app.auth.config import fastapi_users
from app.auth.models import User
from app.dependencies import get_openstack_connection, get_async_session
from app.servers.schemas import (
    Flavor as FlavorSchema,
    Image as ImageSchema,
    Server as ServerSchema,
    Network as NetworkSchema,
    ServerDetailed as ServerDetailedSchema,
    ServerStateActionUpdate,
    ServerStateActionEnum, ServerConfiguration, ServeCreate, ServeUpdate
)
from app.servers.service import send_keypair_email

current_user = fastapi_users.current_user()

router = APIRouter(
    prefix="/servers",
    tags=["servers"]
)


@router.get("/configurations", response_model=list[ServerConfiguration])
async def get_server_configurations(
        _: User = Depends(current_user),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        server_configurations = await db.get_server_configurations(session)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server configurations: {e}")

    return server_configurations


@router.get("/flavors")
async def get_flavors(
        _: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
):
    try:
        flavors = openstack.get_flavors(conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list flavors: {e}")

    return [FlavorSchema.create_from_openstack(flavor) for flavor in flavors]


@router.get("/images")
async def get_images(
        _: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
):
    try:
        images = openstack.get_images(conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list images: {e}")

    return [ImageSchema.create_from_openstack(image) for image in images]


@router.get("/networks")
async def get_networks(
        _: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
):
    try:
        networks = openstack_network.get_networks(conn)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list networks: {e}")

    return [NetworkSchema.create_from_openstack(network) for network in networks]


@router.get("", response_model=list[ServerSchema])
async def get_user_servers_list(
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if user.is_superuser:
            servers = openstack.get_all_servers(conn)
        else:
            server_ids = await db.get_user_server_ids(user, session)
            servers = openstack.get_servers_by_ids(conn, server_ids)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list server: {e}")

    return [ServerSchema.create_from_openstack_server(user.id, server) for server in servers]


@router.get("/{server_id}", response_model=ServerDetailedSchema)
async def get_user_server(
        server_id: uuid.UUID,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session)
):
    try:
        if not await db.is_user_server(server_id, user, session):
            raise HTTPException(status_code=404, detail="Server not found")

        openstack_server = openstack.get_server(conn, str(server_id))
        if openstack_server.image.id:
            image = openstack.get_image(conn, openstack_server.image.id)
    except ResourceNotFound:
        raise HTTPException(status_code=404, detail=f"Server not found")
    except DuplicateResource:
        raise HTTPException(status_code=409, detail=f"Multiple servers found with ID {server_id}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get server: {e}")

    return ServerDetailedSchema.create_from_openstack_server(user.id, openstack_server, image)


@router.post("/from_configuration", response_model=ServerDetailedSchema)
async def create_user_server(
        background_tasks: BackgroundTasks,
        req: ServeCreate,
        user: User = Depends(current_user),
        conn: connection.Connection = Depends(get_openstack_connection),
        session: AsyncSession = Depends(get_async_session),
):
    try:
        server_ids = await db.get_user_server_ids(user, session)
        if len(server_ids) > 10:
            raise HTTPException(status_code=409, detail="Too many servers")

        server_config = await db.get_server_configuration(req.configuration_name, session)

        openstack_server, key_pair = openstack.create_server(conn, str(user.id), server_config)
        if key_pair.private_key:
            await send_keypair_email(background_tasks, user, key_pair, openstack_server)

        await db.insert_user_server(openstack_server.id, user.id, session)
    except ResourceNotFound as e:
        raise HTTPException(status_code=404, detail=f"Resource not found: {e}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to create server: {e}")

    return ServerDetailedSchema.create_from_openstack_server(user.id, openstack_server)


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
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set server state: {e}")
