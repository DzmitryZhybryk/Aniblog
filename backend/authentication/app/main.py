from argparse import ArgumentParser

import uvicorn
from fastapi import status, Request, FastAPI
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.responses import JSONResponse

from .database import database, redis_database
from .initialization.routes import router as init_routers
from .initialization.services import UserStorage
from .models import models
from .users.routes import router as user_routes
from .exception import UnauthorizedException

parser = ArgumentParser(description="Authentication service")

parser.add_argument("--host", help="Authentication host", type=str, default="0.0.0.0")

parser.add_argument("--port", help="Authentication port", type=str, default=8000)

app = FastAPI(docs_url="/api/auth/docs", redoc_url=None, swagger_ui_parameters={"syntaxHighlight.theme": "obsidian"})


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Authentication service",
        version="1.0.0",
        description="Service for authentication users",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
    }
    app.openapi_schema = openapi_schema
    return app.openapi_schema


app.openapi = custom_openapi

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        'http://localhost',
        'http://localhost:3000',
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

app.include_router(user_routes, prefix="/api/auth")
app.include_router(init_routers, prefix="/api/auth")


@app.on_event("startup")
async def on_startup() -> None:
    await models.create_all()
    await database.connect_database()
    redis_database.connect()

    storage = UserStorage()
    await storage.create_initial_roles()
    await storage.create_initial_user()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await database.disconnect_database()
    await redis_database.disconnect()


@app.exception_handler(UnauthorizedException)
def unauthorized_exception_handler(request: Request, exc: UnauthorizedException):
    """Кастомное исключение для неавторизованных пользователей"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content=exc.detail.dict()
    )


# @app.exception_handler(AuthenticationException)
# def non_authentication_exception_handler(request: Request, exc: AuthenticationException):
#     """Кастомное исключения для аутентифицированных пользователей"""
#     return JSONResponse(
#         status_code=status.HTTP_403_FORBIDDEN,
#         content=exc.detail.dict()
#     )


@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    """Кастомное исключение для вывода более информативного ответа 422 ошибки"""
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )


def main():
    args = parser.parse_args()
    uvicorn.run("app.main:app", host=args.host, port=args.port, reload=True)


if __name__ == '__main__':
    # main()
    uvicorn.run("main:app", reload=True)
