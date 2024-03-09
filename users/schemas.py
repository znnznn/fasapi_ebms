from typing import Optional, List

from fastapi_users import schemas, models
from fastapi_users.schemas import PYDANTIC_V2
from pydantic import EmailStr, BaseModel, Field

from common.constants import RoleModel, Role


class CategoryAccessSchema(BaseModel):
    user_id: int
    category_autoid: str


class UserRead(schemas.BaseUser[int]):
    id: models.ID
    email: EmailStr
    first_name: str
    last_name: str
    role: str = Field(alias="role_name")
    is_active: bool = True
    is_superuser: bool = False
    category: Optional[List[CategoryAccessSchema]]

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

