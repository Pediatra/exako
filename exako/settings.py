from pydantic.networks import PostgresDsn
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_HOST: str
    DATABASE_PORT: int
    DATABASE_USER: str
    DATABASE_PASSWORD: str
    DATABASE_NAME: str

    FIEF_CLIENT_ID: str
    FIEF_CLIENT_SCRET: str
    FIEF_DOMAIN: str

    @property
    def DATABASE(self):
        return str(
            PostgresDsn.build(
                scheme='postgresql',
                username=self.DATABASE_USER,
                password=self.DATABASE_PASSWORD,
                host=self.DATABASE_HOST,
                port=self.DATABASE_PORT,
                path=self.DATABASE_NAME,
            )
        )

    @property
    def DATABASE_TEST(self):
        return self.DATABASE.replace(self.DATABASE_NAME, f'{self.DATABASE_NAME}_test')

    class Config:
        env_file = '.env'


settings = Settings()
