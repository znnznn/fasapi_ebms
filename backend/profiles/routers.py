from typing import List

from fastapi import APIRouter, Depends

from common.constants import Role
from database import async_session_maker
from profiles.schemas import CompanyProfileSchema, UserProfileSchema
from profiles.services import CompanyProfileService, UserProfileService
from users.mixins import active_user_with_permission, IsAuthenticatedAs
from users.models import User

router = APIRouter()


@router.get("/company/", response_model=CompanyProfileSchema)
async def get_company_profile(user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER))):
    async with async_session_maker() as session:
        return await CompanyProfileService(db_session=session).get()


@router.post("/company/", response_model=CompanyProfileSchema)
async def create_company_profile(company_profile: CompanyProfileSchema, user: User = Depends(IsAuthenticatedAs(Role.ADMIN, Role.WORKER))):
    async with async_session_maker() as session:
        instance = await CompanyProfileService(db_session=session).get()
        return await CompanyProfileService(db_session=session).update(instance.id, company_profile)


@router.get("/users/", response_model=List[UserProfileSchema])
async def get_user_profiles(user: User = Depends(active_user_with_permission)):
    async with async_session_maker() as session:
        return await UserProfileService(db_session=session).list(user_id=user.id)


@router.post("/users/", response_model=UserProfileSchema)
async def get_user_profile(user_profile: UserProfileSchema, user: User = Depends(active_user_with_permission)):
    async with async_session_maker() as session:
        return await UserProfileService(db_session=session).create(obj=user_profile, user_id=user.id)


@router.delete("/users/")
async def delete_user_profile(user: User = Depends(active_user_with_permission)):
    async with async_session_maker() as session:
        return await UserProfileService(db_session=session).delete(user.id)
