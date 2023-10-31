# from pydantic import PostgresDsn
from starlette.config import Config
from starlette.datastructures import Secret

config = Config()


class Settings:
    # POSTGRES_USER = config("POSTGRES_USER", cast=str)
    # POSTGRES_PASSWORD = config("POSTGRES_PASSWORD", cast=Secret)
    # POSTGRES_SERVER = config("POSTGRES_SERVER", cast=str)
    # POSTGRES_PORT = config("POSTGRES_PORT", cast=str, default="5432")
    # POSTGRES_DB = config("POSTGRES_DB", cast=str)

    # SQLALCHEMY_DATABASE_URI: str = PostgresDsn.build(
    #     scheme="postgresql",
    #     user=POSTGRES_USER,
    #     password=str(POSTGRES_PASSWORD),
    #     host=POSTGRES_SERVER,
    #     port=POSTGRES_PORT,
    #     path=f"/{POSTGRES_DB or ''}",
    # )

    NOROVIRUS_BLAST_DATABASE_URI: str = config('NOROVIRUS_BLAST_DATABASE_URI', cast=str, default='sqlite:///app.db')


settings = Settings()
