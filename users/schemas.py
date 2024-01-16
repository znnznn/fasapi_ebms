from typing import Optional

from fastapi_users import schemas, models
from fastapi_users.schemas import PYDANTIC_V2
from pydantic import EmailStr, BaseModel


class UserRead(schemas.BaseUser[int]):
    id: models.ID
    email: EmailStr
    is_active: bool = True
    is_superuser: bool = False

    # if PYDANTIC_V2:  # pragma: no cover
    #     model_config = ConfigDict(from_attributes=True)  # type: ignore
    # else:  # pragma: no cover

    class Config:
        from_attributes = True


class UserCreate(schemas.BaseUserCreate):
    email: str
    password: str
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False


class UserUpdate(schemas.BaseUserUpdate):
    pass

