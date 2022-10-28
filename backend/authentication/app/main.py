import uvicorn
from fastapi import status, Request, FastAPI
from fastapi.responses import JSONResponse
from argparse import ArgumentParser
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder

from .users.routes import router as user_routes
from .database import connect_database, disconnect_database
from .models import models
from .users.services import has_db_user, create_initial_user, has_db_roles, create_users_roles
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


@app.on_event("startup")
async def on_startup() -> None:
    await models.create_all()
    await connect_database()

    db_has_roles = await has_db_roles()
    if not db_has_roles:
        await create_users_roles()

    db_has_user = await has_db_user()
    if not db_has_user:
        await create_initial_user()


@app.on_event("shutdown")
async def on_shutdown() -> None:
    await disconnect_database()


@app.exception_handler(UnauthorizedException)
def exception_handler(request: Request, exc: UnauthorizedException):
    """Кастомное исключение для неавторизованных пользователей"""
    return JSONResponse(
        status_code=status.HTTP_401_UNAUTHORIZED,
        content={"message": "Incorrect username or password"}
    )


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
    main()
    # uvicorn.run("main:app", reload=True)
