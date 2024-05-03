from decouple import config
from pydantic import Field
from pydantic_settings import BaseSettings

SECRET_KEY = config("SECRET_KEY", cast=str)

TOKEN_CREDENTIAL = config("TOKEN_CREDENTIAL", cast=str)

FILTERING_DATA_STARTING_YEAR = config('FILTERING_DATA_STARTING_YEAR', default='2023-01-01', cast=str)
LIST_EXCLUDED_PROD_TYPES = ("", "Vents")

ALGORITHM = "SHA256"
ACCESS_TOKEN_LIFETIME_SECONDS = config("ACCESS_TOKEN_LIFETIME_SECONDS", cast=int, default=3600)

RESEND_API_KEY = config('RESEND_API_KEY', default='')
RESEND_FROM_EMAIL = config('RESEND_FROM_EMAIL', default='')

FRONTEND_HOST = config('FRONTEND_HOST', default='dev-embs.com', cast=str)

EBMS_API_PASSWORD = config("EBMS_API_PASSWORD", cast=str)
EBMS_API_LOGIN = config("EBMS_API_LOGIN", cast=str)
EBMS_API_URL = config("EBMS_API_URL", cast=str)


class EBMSDatabase(BaseSettings):
    DB_USER: str = Field(alias="EBMS_DB_USER", default="")
    DB_PASS: str = Field(alias="MSSQL_SA_PASSWORD", default="postgres")
    DB_HOST: str = Field(alias="EBMS_DB_HOST", default="localhost")
    DB_PORT: int = Field(alias="EBMS_DB_PORT", default=1433)
    DB_NAME: str = Field(alias="EBMS_DB_NAME", default="mssql")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


class DataBase(BaseSettings):
    DB_USER: str = Field(alias="DB_USER", default="postgres")
    DB_PASS: str = Field(alias="DB_PASS", default="postgres")
    DB_HOST: str = Field(alias="DB_HOST", default="localhost")
    DB_PORT: int = Field(alias="DB_PORT", default=5432)
    DB_NAME: str = Field(alias="DB_NAME", default="stock")

    class Config:
        env_file = ".env"
        case_sensitive = True
        extra = "allow"


REDIS_PASSWORD = config("REDIS_PASSWORD", default="")
REDIS_HOST = config("REDIS_HOST", default="redis")
REDIS_PORT = config("REDIS_PORT", default=6379)
REDIS_DB = config("REDIS_DB", default=0)
REDIS_URL = config("REDIS_URL", default="redis://redis:6379")


EBMS_DB = EBMSDatabase()
Default_DB = DataBase()
