from sqlalchemy import create_engine
from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine
from sqlalchemy.orm import sessionmaker

from app.config import settings

DATABASE_ASYNC_URL = f'{"postgresql+asyncpg"}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_schema}'
DATABASE_URL = f'{"postgresql"}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_schema}'

async_engine = create_async_engine(DATABASE_ASYNC_URL)
async_session_maker = async_sessionmaker(async_engine, expire_on_commit=False)

sync_engine = create_engine(DATABASE_URL)
session_maker = sessionmaker(bind=sync_engine, expire_on_commit=False)