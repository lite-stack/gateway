import uuid

from sqlalchemy import select, delete
from sqlalchemy.ext.asyncio import AsyncSession

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


async def get_user_server_ids(
        user: User,
        session: AsyncSession,
) -> list:
    query = select(Server).where(Server.owner_id == user.id)
    result = await session.execute(query)

    return [server[0].openstack_id for server in result.all()]


async def insert_user_server(
        server_id: uuid.UUID,
        user_id: uuid.UUID,
        session: AsyncSession,
):
    db_server = Server(openstack_id=server_id, owner_id=user_id)
    session.add(db_server)
    await session.commit()


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
