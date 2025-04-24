import base64
import os

from dotenv import load_dotenv
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_USER = os.getenv("DB_USER", "postgres")
DB_NAME = os.getenv("DB_NAME", "postgres")

EMAIL_PRIMEIRO_USUARIO = os.getenv("EMAIL_PRIMEIRO_USUARIO")
SENHA_PRIMEIRO_USUARIO = os.getenv("SENHA_PRIMEIRO_USUARIO")
CPF_PRIMEIRO_USUARIO = os.getenv("CPF_PRIMEIRO_USUARIO")

AES_KEY = base64.b64decode(os.getenv("APP_AES_KEY"))

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("ALGORITHM")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", default="30"))

oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl="api/token",
    scopes={"me": "Read information about the current user.", "items": "Read items."},
)
