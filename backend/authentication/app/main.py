import uvicorn

from argparse import ArgumentParser
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from .routes import router as authentication_routes

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

app.include_router(authentication_routes, prefix="/api/auth", tags=["Users"])


def main():
    args = parser.parse_args()
    uvicorn.run("main:app", host=args.host, port=args.port, reload=True)


if __name__ == '__main__':
    # main()
    uvicorn.run("main:app", reload=True)
