from typing import Optional, List
from fastapi_users import schemas, models
from pydantic import EmailStr, BaseModel, Field, root_validator, model_validator

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


class UserCreate(schemas.CreateUpdateDictModel):
    email: str
    password: str
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True


class UserUpdate(schemas.BaseUserUpdate):
    pass


class UsersPaginatedSchema(BaseModel):
    count: int
    results: List[UserRead]


class PasswordResetConfirmationSchema(BaseModel):
    token: str
    uid64: str
    new_password1: str
    new_password2: str


class UserReadShortSchema(BaseModel):
    id: models.ID
    email: EmailStr
    first_name: str
    last_name: str
    role: str = Field(alias="role_name")

    class Config:
        from_attributes = True


class UserPasswordChangeSchema(BaseModel):
    old_password: str
    new_password1: str
    new_password2: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
