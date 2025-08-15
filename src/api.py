from contextlib import asynccontextmanager
from datetime import timedelta
from typing import Annotated

from fastapi import FastAPI, APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm

from src.banco_de_dados import listar_schemas_existentes
from src.constantes import ACCESS_TOKEN_EXPIRE_MINUTES
from src.executores import decrypt_email
from src.models import UsuariosPublicos
from src.repositorios import CompanyRepository, UserRepository
from src.schemas import (
    LerEmpresaSchema,
    CadastrarEmpresaSchema,
    LerUsuarioSchema,
    CadastrarUsuarioSchema,
    Token,
)
from src.seguranca import (
    create_access_token,
    get_current_user,
    authenticate_user,
    current_user,
)


@asynccontextmanager
async def lifespan(app: FastAPI):
    from src.banco_de_dados import criar_primeira_empresa_e_usuario

    criar_primeira_empresa_e_usuario()
    yield


app = FastAPI(
    title="API Sistema Base Backend",
    description="APIs REST",
    version="0.1.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
    swagger_ui_parameters={"persistAuthorization": True},
)


@app.get("/")
async def test():
    return {"message": "API está no ar!"}


router_seguranca = APIRouter(prefix="/api", tags=["Login"])


@router_seguranca.post("/token")
async def login_for_access_token(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
) -> Token:
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=400, detail="Incorrect username or password")
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={
            "email": decrypt_email(user.email_enc),
            "id_empresa": str(user.empresa_id),
            "scopes": form_data.scopes,
        },
        expires_delta=access_token_expires,
    )
    return Token(access_token=access_token, token_type="bearer")


@router_seguranca.get("/users/me/", response_model=LerUsuarioSchema)
async def read_users_me(
    current_user: Annotated[UsuariosPublicos, Depends(get_current_user)],
):
    return current_user


router_empresa = APIRouter(
    prefix="/api/v1", tags=["Empresas"], dependencies=[Depends(get_current_user)]
)


@router_empresa.get("/empresas", response_model=list[LerEmpresaSchema])
async def listar_empresas():
    # obter todos os schemas
    schemas = listar_schemas_existentes()

    empresas = [e for schema in schemas for e in CompanyRepository().list(schema)]
    return empresas


@router_empresa.post("/empresa", response_model=LerEmpresaSchema)
async def cadastrar_empresa(payload: CadastrarEmpresaSchema):
    empresa = CompanyRepository().create(payload.nome)
    return empresa


router_usuario = APIRouter(
    prefix="/api/v1", tags=["Usuários"], dependencies=[Depends(get_current_user)]
)


@router_usuario.get("/usuarios", response_model=list[LerUsuarioSchema])
async def listar_usuarios():
    usuario_atual = current_user.get()

    usuarios = UserRepository().list(usuario_atual.empresa_id)
    return usuarios


@router_usuario.post("/usuario", response_model=LerUsuarioSchema)
async def cadastrar_usuarios(
    payload: CadastrarUsuarioSchema,
):
    usuario_atual = current_user.get()

    usuario = UserRepository().create(
        payload.email, payload.senha, usuario_atual.empresa_id
    )
    return usuario


app.include_router(router_seguranca)
app.include_router(router_empresa)
app.include_router(router_usuario)
