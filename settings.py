from decouple import config
from pydantic import Field
from pydantic_settings import BaseSettings

SECRET_KEY = config("SECRET_KEY", cast=str)

# DB_USER = config("DB_USER", cast=str, default="postgres")
# DB_PASS = config("MSSQL_SA_PASSWORD", cast=str, default="postgres")
# DB_HOST = config("DB_HOST", cast=str, default="localhost")
# DB_PORT = config("DB_PORT", cast=int, default=5432)
# DB_NAME = config("DB_NAME", cast=str, default="stock")

ALGORITHM = "SHA256"
ACCESS_TOKEN_EXPIRE_MINUTES = config("ACCESS_TOKEN_EXPIRE_MINUTES", cast=int, default=30)


class EBMSDatabase(BaseSettings):
    DB_USER: str = Field(alias="EBMS_DB_USER")
    DB_PASS: str = Field(alias="MSSQL_SA_PASSWORD")
    DB_HOST: str = Field(alias="EBMS_DB_HOST")
    DB_PORT: int = Field(alias="EBMS_DB_PORT")
    DB_NAME: str = Field(alias="EBMS_DB_NAME")


class DataBase(BaseSettings):
    DB_USER: str = Field(alias="DB_USER")
    DB_PASS: str = Field(alias="DB_PASS")
    DB_HOST: str = Field(alias="DB_HOST")
    DB_PORT: int = Field(alias="DB_PORT")
    DB_NAME: str = Field(alias="DB_NAME")


EBMS_DB = EBMSDatabase()
Default_DB = DataBase()
