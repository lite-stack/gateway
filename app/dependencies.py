from functools import lru_cache
from typing import AsyncGenerator

from fastapi import Header, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import async_session_maker
from app.openstack.config import get_connection
from config import Settings


@lru_cache()
def get_settings():
    return Settings()


async def get_async_session() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session


async def get_jwt(token: str = Header(...)):
    if token != 'fake-super-secret-token':
        raise HTTPException(status_code=400, detail='X-Token header invalid')


async def get_openstack_connection():
    try:
        conn = await get_connection()
        return conn
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to connect to OpenStack: {e}")
