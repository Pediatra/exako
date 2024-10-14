from contextlib import asynccontextmanager
from typing import AsyncGenerator

from fastapi import FastAPI
from tortoise import Tortoise
from tortoise.contrib.fastapi import RegisterTortoise

from exako.apps.user.schema import UserCreate, UserRead
from exako.apps.user.security import auth_jwt_backend, auth_cookie_backend
from exako.apps.user.router import fastapi_users
from exako.settings import register_orm, TORTOISE_MODULES, TORTOISE_CONNECTION


@asynccontextmanager
async def lifespan_test(app: FastAPI) -> AsyncGenerator[None, None]:
    async with RegisterTortoise(
        app=app,
        config={
            'apps': TORTOISE_MODULES,
            'connections': {**TORTOISE_CONNECTION, 'database': 'exako_test'},
        },
        generate_schemas=True,
        add_exception_handlers=True,
    ):
        yield
    await Tortoise._drop_databases()


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if getattr(app.state, 'testing', None):
        async with lifespan_test(app) as _:
            yield
    else:
        async with register_orm(app):
            yield


app = FastAPI(lifespan=lifespan)

app.include_router(
    fastapi_users.get_auth_router(auth_jwt_backend),
    prefix='/auth/jwt',
    tags=['auth'],
)
app.include_router(
    fastapi_users.get_auth_router(auth_cookie_backend),
    prefix='/auth/cookie',
    tags=['auth'],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix='/auth',
    tags=['auth'],
)
