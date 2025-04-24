from contextlib import asynccontextmanager

from fastapi import FastAPI, APIRouter
from pydantic import UUID4

from src.banco_de_dados import listar_schemas_existentes
from src.repositorios import CompanyRepository, UserRepository
from src.schemas import (
    LerEmpresaSchema,
    CadastrarEmpresaSchema,
    LerUsuarioSchema,
    CadastrarUsuarioSchema,
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
)


@app.get("/")
async def test():
    return {"message": "API está no ar!"}


router_empresa = APIRouter(prefix="/api/v1", tags=["Empresas"])


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


router_usuario = APIRouter(prefix="/api/v1", tags=["Usuários"])


@router_usuario.get("/usuarios", response_model=list[LerUsuarioSchema])
async def listar_usuarios(schema_id: UUID4 | None = None):
    usuarios = UserRepository().list(schema_id)
    return usuarios


@router_usuario.post("/usuario", response_model=LerUsuarioSchema)
async def cadastrar_usuarios(
    payload: CadastrarUsuarioSchema,
):
    usuario = UserRepository().create(payload.email, payload.senha, payload.empresa_id)
    return usuario


app.include_router(router_empresa)
app.include_router(router_usuario)
