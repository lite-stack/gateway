import uuid

from sqlalchemy import select, delete, update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from app.auth.models import User
from app.servers.models import Server, ServerConfig


async def is_user_server(
        server_id: uuid.UUID,
        user: User,
        session: AsyncSession,
) -> bool:
    query = select(Server).where(Server.openstack_id == server_id).limit(1)

    if not user.is_superuser:
        query = query.where(Server.owner_id == user.id)

    result = await session.execute(query)

    return len(result.all()) != 0


async def get_user_server(
        user: User,
        openstack_id: str,
        session: AsyncSession,
) -> Server:
    query = select(Server).where(Server.owner_id == user.id).where(Server.openstack_id == openstack_id)
    result = await session.execute(query)

    return result.scalar_one()


async def get_user_servers(
        user: User,
        session: AsyncSession,
) -> list:
    query = select(Server).where(Server.owner_id == user.id)
    result = await session.execute(query)

    return [server[0] for server in result.all()]


async def get_all_servers(
        session: AsyncSession,
) -> list:
    result = await session.execute(select(Server))

    return [server[0] for server in result.all()]


async def insert_user_server(
        server_id: uuid.UUID,
        user_id: uuid.UUID,
        image: str,
        session: AsyncSession,
):
    db_server = Server(openstack_id=server_id, owner_id=user_id, image=image)
    session.add(db_server)
    await session.commit()


def update_user_server(
        server: Server,
        session: Session,
):
    db_server = session.query(Server).filter_by(openstack_id=server.openstack_id).first()
    db_server.tags = server.tags
    session.commit()


async def delete_user_server(
        server_id: uuid.UUID,
        session: AsyncSession,
):
    stmt = delete(Server).where(Server.openstack_id == server_id)
    await session.execute(stmt)
    await session.commit()


async def get_server_configurations(
        session: AsyncSession,
) -> list[ServerConfig]:
    query = select(ServerConfig)
    result = await session.execute(query)

    return [server[0] for server in result.all()]


async def get_server_configuration(
        name: str,
        session: AsyncSession,
) -> ServerConfig:
    query = select(ServerConfig).where(ServerConfig.name == name)
    result = await session.execute(query)

    return result.scalar_one()
