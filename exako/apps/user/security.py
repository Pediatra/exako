from fastapi_users.authentication import (
    AuthenticationBackend,
    BearerTransport,
    CookieTransport,
    JWTStrategy,
)

from exako.settings import settings

bearer_transport = BearerTransport(tokenUrl='auth/jwt/login')
cookie_transport = CookieTransport(
    cookie_max_age=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60
)


def get_jwt_strategy() -> JWTStrategy:
    return JWTStrategy(
        secret=settings.SECRET_KEY,
        lifetime_seconds=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
    )


auth_jwt_backend = AuthenticationBackend(
    name='jwt',
    transport=bearer_transport,
    get_strategy=get_jwt_strategy,
)
auth_cookie_backend = AuthenticationBackend(
    name='cookie',
    transport=cookie_transport,
    get_strategy=get_jwt_strategy,
)
