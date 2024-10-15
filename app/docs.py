from fastapi.openapi.docs import (
    get_redoc_html,
    get_swagger_ui_html,
    get_swagger_ui_oauth2_redirect_html,
)

from .config import settings


__all__ = ("custom_swagger_ui_html", "swagger_ui_redirect", "redoc_html")


async def custom_swagger_ui_html(
    title: str, openapi_url: str, swagger_ui_oauth2_redirect_url: str
):
    return get_swagger_ui_html(
        openapi_url=openapi_url,  # type: ignore
        title=title,
        oauth2_redirect_url=swagger_ui_oauth2_redirect_url,
        swagger_js_url=f"{settings.STATIC_URL}/swagger-ui-bundle.js",
        swagger_css_url=f"{settings.STATIC_URL}/swagger-ui.css",
        swagger_favicon_url=f"{settings.STATIC_URL}/favicon.png",
    )


async def swagger_ui_redirect():
    return get_swagger_ui_oauth2_redirect_html()


async def redoc_html(
    title: str,
    openapi_url: str,
):
    return get_redoc_html(
        openapi_url=openapi_url,
        title=title,
        redoc_js_url=f"{settings.STATIC_URL}/redoc.standalone.js",
        with_google_fonts=False,
        redoc_favicon_url=f"{settings.STATIC_URL}/favicon.png",
    )
