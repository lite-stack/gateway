from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from app.auth.config import auth_backend
from app.auth.config import fastapi_users
from app.auth.schemas import UserRead, UserCreate, UserUpdate
from app.dependencies import get_settings
from app.servers.router import router as servers_router
from config import APP_CONFIG, Settings
from app.auth.router import router as user_router

app = FastAPI(**APP_CONFIG)

app.add_middleware(
    CORSMiddleware,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    user_router,
    prefix="/users",
    tags=["users"],
)

app.include_router(servers_router)


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
