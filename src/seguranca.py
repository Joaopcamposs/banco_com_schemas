from contextvars import ContextVar
from datetime import timedelta, datetime
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException
from fastapi.security import SecurityScopes
from passlib.exc import InvalidTokenError
from pydantic import ValidationError
from starlette import status

from src.constantes import SECRET_KEY, ALGORITHM, oauth2_scheme
from src.executores import verify_password
from src.models import Usuario, UsuariosPublicos
from src.schemas import TokenData

current_user: ContextVar["Usuario"] = ContextVar("current_user")


def authenticate_user(username: str, password: str) -> None | UsuariosPublicos:
    from src.repositorios import UserRepository

    usuario = UserRepository().get_public_user_by_email(username)

    if not usuario:
        return None
    if not verify_password(password, usuario.password_hash):
        return None
    return usuario


def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now() + expires_delta
    else:
        expire = datetime.now() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


async def get_current_user(
    security_scopes: SecurityScopes, token: Annotated[str, Depends(oauth2_scheme)]
):
    from src.repositorios import UserRepository

    if security_scopes.scopes:
        authenticate_value = f'Bearer scope="{security_scopes.scope_str}"'
    else:
        authenticate_value = "Bearer"
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": authenticate_value},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email = payload.get("email")
        empresa_id = payload.get("id_empresa")
        if email is None:
            raise credentials_exception
        token_scopes = payload.get("scopes", [])
        token_data = TokenData(scopes=token_scopes, username=email)
    except (InvalidTokenError, ValidationError):
        raise credentials_exception

    user = UserRepository().get_user_by_email_and_empresa_id(email, empresa_id)

    if user is None:
        raise credentials_exception
    for scope in security_scopes.scopes:
        if scope not in token_data.scopes:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Not enough permissions",
                headers={"WWW-Authenticate": authenticate_value},
            )
    current_user.set(user)

    return user
