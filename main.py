from typing import Union, Optional, List

from fastapi import FastAPI, Depends
from pydantic import BaseModel
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from users.auth import auth_backend
from users.mixins import fastapi_users, current_user
from users.schemas import UserRead, UserCreate
from origin_db.routers import router as origin_router


class ErrorResponse(BaseModel):
    errors: Optional[List[str]]


app = FastAPI(
    title="FastAPI", debug=True, default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["auth"],
)

app.include_router(
    fastapi_users.get_reset_password_router(),
    prefix="/auth",
)

app.include_router(origin_router)
