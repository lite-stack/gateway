from sqlalchemy.ext.asyncio import async_sessionmaker, create_async_engine

from app.config import settings

DATABASE_URL = f'{"postgresql+asyncpg"}://{settings.db_user}:{settings.db_password}@{settings.db_host}:{settings.db_port}/{settings.db_schema}'

engine = create_async_engine(DATABASE_URL)
async_session_maker = async_sessionmaker(engine, expire_on_commit=False)
