from typing import Optional, List

from fastapi import FastAPI
from fastapi_pagination.utils import disable_installed_extensions_check
from pydantic import BaseModel
from starlette.middleware.cors import CORSMiddleware
from starlette.responses import JSONResponse
from origin_db.routers import router as origin_router
from stages.routers import router as stages_router
from profiles.routers import router as profiles_router
from users.routers import router as users_router
from users.auth_routers import router as auth_router
from websockets_connection.routers import router as ws_router


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
    swagger_ui_parameters={"deepLinking": False}
)

origins = [
    "http://localhost",
    "http://localhost:8080",
    "https://dev-ebms.fun",
    "dev-ebms.com"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
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


app.include_router(origin_router)

app.include_router(stages_router)

app.include_router(profiles_router, prefix="/profiles", tags=["profiles"])

app.include_router(users_router, prefix="/users", tags=["users"])

app.include_router(auth_router, prefix="/token", tags=["token"])

app.include_router(ws_router, prefix="/ws", tags=["ws"])
