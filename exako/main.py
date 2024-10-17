from fastapi import FastAPI
from fastapi_pagination import add_pagination

from exako.apps.term.routers.term import term_router
from exako.apps.user.router import fastapi_users
from exako.apps.user.schema import UserCreate, UserRead
from exako.apps.user.security import auth_cookie_backend, auth_jwt_backend
from exako.core.middleware import LanguageMiddleware

app = FastAPI()

app.add_middleware(LanguageMiddleware)

add_pagination(app)

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

app.include_router(term_router, prefix='/term', tags=['term'])
