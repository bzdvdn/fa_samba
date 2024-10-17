import os

from dotenv import load_dotenv

PROJECT_NAME = "Samba-AD API"
PROJECT_DESCRIPTION = "samba ad admin api"

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

dotenv_path = f"{BASE_DIR}/.env"
if os.path.exists(dotenv_path):
    load_dotenv(dotenv_path)


SECRET_KEY = os.getenv("SECRET_KEY", "")
SECRET_SALT = os.getenv(
    "SECRET_SALT",
)
if SECRET_SALT and len(SECRET_SALT) != 16:
    raise RuntimeError("SECRET_SALT must be 16 symbols")
SAMBA_HOST = os.getenv("SAMBA_HOST")
if not SAMBA_HOST:
    raise RuntimeError("SAMBA_HOST cant be empty.")
BASE_PREFIX = os.environ.get("URL_HOST_PATH_PREFIX", "/")
if BASE_PREFIX and not BASE_PREFIX.endswith("/"):
    raise RuntimeError("URL_HOST_PATH_PREFIX must be endswith `/`, like `app/`")
API_V1_STR = f"{BASE_PREFIX}api"
OPEN_API_URL = f"{BASE_PREFIX}openapi.json/"
DOCS_URL = f"{BASE_PREFIX}docs/"
REDOC_URL = f"{BASE_PREFIX}redoc/"
SWAGGER_OAUTH_REDIRECT_URL = f"{BASE_PREFIX}docs/oauth2-redirect/"
STATIC_URL = f"{BASE_PREFIX}static/"

ACCESS_TOKEN_EXPIRE_SECONDS = int(os.getenv("ACCESS_TOKEN_EXPIRE_SECONDS", 300))
REFRESH_TOKEN_EXPIRE_SECONDS = int(os.getenv("REFRESH_TOKEN_EXPIRE_SECONDS", 86400))
