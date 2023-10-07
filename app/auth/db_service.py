from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.models import User


async def get_users(
        session: AsyncSession,
) -> list[User]:
    query = select(User)
    result = await session.execute(query)

    return [server[0] for server in result.all()]
