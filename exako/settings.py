from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int

    @property
    def DATABASE(self):
        return str(
            PostgresDsn.build(
                scheme='postgresql+asyncpg',
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                path=self.DATABASE_NAME,
            )
        )

    @property
    def DATABASE_TEST(self):
        return str(
            PostgresDsn.build(
                scheme='postgresql',
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                path=f'{self.DATABASE_NAME}_test',
            )
        )

    class Config:
        env_file = '.env'


settings = Settings()
