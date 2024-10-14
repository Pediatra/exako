from functools import partial

from tortoise.contrib.fastapi import RegisterTortoise

from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str
    
    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    class Config:
        env_file = '.env'


settings = Settings()

TORTOISE_CONNECTION = {
    'default': {
        'engine': 'tortoise.backends.asyncpg',
        'credentials': {
            'host': settings.DATABASE_HOST,
            'port': settings.DATABASE_PORT,
            'user': settings.DATABASE_USER,
            'password': settings.DATABASE_PASSWORD,
            'database': settings.DATABASE_NAME,
        },
    },
}

TORTOISE_MODULES = {
    'models': [
        'exako.apps.term.models',
        'exako.apps.exercise.models',
        'exako.apps.cardset.models',
        'exako.apps.user.models',
        'aerich.models',
    ]
}

TORTOISE_ORM = {
    'apps': {'models': TORTOISE_MODULES},
    'connections': TORTOISE_CONNECTION,
}

register_orm = partial(
    RegisterTortoise,
    config=TORTOISE_ORM,
    add_exception_handlers=True,
)
