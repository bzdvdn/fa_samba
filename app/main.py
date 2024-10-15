from starlette.middleware.sessions import SessionMiddleware

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic.error_wrappers import ValidationError


from .config import settings
from .docs import custom_swagger_ui_html, redoc_html, swagger_ui_redirect
from .routers import api_router


app = FastAPI(
    title=settings.PROJECT_NAME,
    description=settings.PROJECT_DESCRIPTION,
    version="1",
    docs_url=None,
    redoc_url=None,
    openapi_url=settings.OPEN_API_URL,
)


app.mount(settings.STATIC_URL, StaticFiles(directory="app/static"), name="static")


app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SessionMiddleware, secret_key=settings.SECRET_KEY)


@app.get(settings.DOCS_URL, include_in_schema=False)
async def get_swagger_ui_html():
    return await custom_swagger_ui_html(
        settings.PROJECT_NAME,
        settings.OPEN_API_URL,
        settings.SWAGGER_OAUTH_REDIRECT_URL,
    )


@app.get(settings.SWAGGER_OAUTH_REDIRECT_URL, include_in_schema=False)
async def get_swagger_ui_redirect():
    return await swagger_ui_redirect()


@app.get(settings.REDOC_URL, include_in_schema=False)
async def get_redoc_html():
    return await redoc_html(
        openapi_url=settings.OPEN_API_URL,
        title=settings.PROJECT_NAME,
    )


app.include_router(api_router, prefix=settings.API_V1_STR)
