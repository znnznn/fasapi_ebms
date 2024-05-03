from contextlib import asynccontextmanager
from typing import Optional, List

from fastapi import FastAPI
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from origin_db.routers import router as origin_router
from stages.routers import router as stages_router
from profiles.routers import router as profiles_router
from users.routers import router as users_router
from users.auth_routers import router as auth_router
from websockets_connection.managers import connection_manager
from websockets_connection.routers import router as ws_router


class ErrorResponse(BaseModel):
    errors: Optional[List[str]]


@asynccontextmanager
async def websocketlifespan(app: FastAPI):
    await connection_manager.connect_broadcaster()
    yield
    await connection_manager.disconnect_broadcaster()


app = FastAPI(
    title="Wiseline Metals", debug=True, default_response_class=JSONResponse,
    responses={
        400: {"model": ErrorResponse},
        401: {"model": ErrorResponse},
        403: {"model": ErrorResponse},
        404: {"model": ErrorResponse},
        500: {"model": ErrorResponse},
    },
    docs_url='/docs',
    redoc_url='/redoc',
    openapi_url='/openapi.json',
    swagger_ui_parameters={"deepLinking": False},
    lifespan=websocketlifespan
)


origins = [
    "*",
    "http://localhost",
    "http://localhost:3000/",
    "http://localhost:8000",
    "https://dev-ebms.fun",
    "https://dev-ebms.fun/",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


disable_installed_extensions_check()


app.include_router(origin_router)

app.include_router(stages_router)

app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])

app.include_router(users_router, prefix="/users", tags=["users"])

app.include_router(auth_router, prefix="/token", tags=["token"])

app.include_router(ws_router, prefix="/ws", tags=["ws"])
