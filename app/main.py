from fastapi import FastAPI, Depends
from app.auth.config import fastapi_users

from app.auth.config import auth_backend
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from config import APP_CONFIG, Settings
from app.dependencies import get_settings

app = FastAPI(**APP_CONFIG)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

app.include_router(
    fastapi_users.get_users_router(UserRead, UserUpdate),
    prefix="/users",
    tags=["users"],
)


@app.get('/', tags=['root'])
async def root() -> dict:
    '''' Root path get function
    :return: {'api': 'FastAPI Template'}
    '''
    return {'status': 'ok'}


@app.get('/log', tags=['root'])
async def insert_log(
        msg: str,
        settings: Settings = Depends(get_settings)
) -> dict:
    settings.info_logger.info(msg)
    return {'msg': 'message logged successfully'}


@app.get('/db', tags=['root'])
async def get_db(
        settings: Settings = Depends(get_settings)
) -> dict:
    return {'db': settings.db_engine}
