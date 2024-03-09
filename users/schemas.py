from typing import Optional, List
from fastapi_users import schemas, models
from pydantic import EmailStr, BaseModel, Field

from common.constants import RoleModel, Role
from profiles.schemas import UserProfileSchema


class CategoryAccessSchema(BaseModel):
    user_id: int
    category_autoid: str

    class Config:
        from_attributes = True

class UserRead(schemas.BaseUser[int]):
    id: models.ID
    email: EmailStr
    first_name: str
    last_name: str
    role: str = Field(alias="role_name")
    category: Optional[List[CategoryAccessSchema]]
    user_profiles: Optional[List[UserProfileSchema]]

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

