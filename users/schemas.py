from typing import Optional, List
from fastapi_users import schemas, models
from fastapi_users.schemas import model_dump
from pydantic import EmailStr, BaseModel, Field, root_validator, model_validator, field_validator

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
    role_name: str = Field(serialization_alias="role")
    category: Optional[List[CategoryAccessSchema]]
    user_profiles: Optional[List[UserProfileSchema]]

    class Config:
        from_attributes = True


class UserCreate(schemas.CreateUpdateDictModel):
    email: EmailStr
    password: Optional[str] = None
    role: Optional[RoleModel] = Field(default=RoleModel.worker)
    first_name: str
    last_name: str
    is_active: Optional[bool] = True
    is_superuser: Optional[bool] = False

    class Config:
        orm_mode = True
        from_attributes = True


class UserUpdate(schemas.BaseUserUpdate):
    email: Optional[EmailStr] = None
    is_active: Optional[bool] = None
    role: Optional[RoleModel] = None
    first_name: Optional[str] = None
    last_name: Optional[str] = None

    def create_update_dict(self):
        return model_dump(
            self,
            exclude_unset=True,
            exclude={
                "id",
                "is_superuser",
                "is_active",
                "is_verified",
                "oauth_accounts",
                "role",
            },
        )

    def create_update_dict_superuser(self):
        return model_dump(self, exclude_unset=True, exclude={"id"})


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
    is_active: bool
    role_name: str = Field(serialization_alias="role")

    class Config:
        from_attributes = True


class UserPasswordChangeSchema(BaseModel):
    old_password: str
    new_password1: str
    new_password2: str


class UserLoginSchema(BaseModel):
    email: EmailStr
    password: str
