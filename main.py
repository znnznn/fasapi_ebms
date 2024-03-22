from typing import Union, Optional, List

from fastapi import FastAPI, Depends
from fastapi.exception_handlers import http_exception_handler, request_validation_exception_handler
from fastapi.exceptions import RequestValidationError
from fastapi_pagination import add_pagination
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles
from starlette.exceptions import HTTPException as StarletteHTTPException

from users.auth import auth_backend_refresh
from users.mixins import fastapi_users, current_user
from users.schemas import UserRead, UserCreate, UserUpdate
from origin_db.routers import router as origin_router
from stages.routers import router as stages_router
from profiles.routers import router as profiles_router
from users.routers import router as users_router
from users.auth_routers import router as auth_router


class ErrorResponse(BaseModel):
    errors: Optional[List[str]]


app = FastAPI(
    title="Wiseline Metals", debug=True, default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
)

origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)



# @app.exception_handler(Exception)
# async def validation_exception_handler(request: Request, exc: Exception):
#     # Change here to Logger
#     print("++++++++++++++++++++++++++++++++++++")
#     return JSONResponse(
#         status_code=500,
#         content={
#             "message": (
#                 f"Failed method {request.method} at URL {request.url}."
#                 f" Exception message is {exc!r}."
#             )
#         },
#     )


disable_installed_extensions_check()


# app.include_router(
#     fastapi_users.get_auth_router(auth_backend_refresh),
#     prefix="/token",
#     tags=["token"],
# )

app.include_router(origin_router)

app.include_router(stages_router)

app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])

app.include_router(users_router, prefix="/users", tags=["users"])

app.include_router(auth_router, prefix="/token", tags=["token"])
