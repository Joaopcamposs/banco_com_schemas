import os

from dotenv import load_dotenv

load_dotenv()

DB_HOST = os.getenv("DB_HOST", "localhost")
DB_PASSWORD = os.getenv("DB_PASSWORD", "password")
DB_USER = os.getenv("DB_USER", "postgres")
DB_NAME = os.getenv("DB_NAME", "postgres")

EMAIL_PRIMEIRO_USUARIO = os.getenv("EMAIL_PRIMEIRO_USUARIO")
SENHA_PRIMEIRO_USUARIO = os.getenv("SENHA_PRIMEIRO_USUARIO")
CPF_PRIMEIRO_USUARIO = os.getenv("CPF_PRIMEIRO_USUARIO")
