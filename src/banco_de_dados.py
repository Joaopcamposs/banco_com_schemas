from __future__ import annotations

import os
from contextlib import contextmanager
from uuid import uuid4, UUID

from sqlalchemy import create_engine, text
from sqlalchemy.orm import (
    sessionmaker,
    declarative_base,
)

from src.constantes import (
    DB_HOST,
    DB_PASSWORD,
    DB_USER,
    DB_NAME,
    EMAIL_PRIMEIRO_USUARIO,
    SENHA_PRIMEIRO_USUARIO,
)


def obter_uri_do_banco_de_dados(eh_teste: bool = False) -> str:
    ambiente_de_teste = eh_teste or os.getenv("TEST_ENV")
    em_docker = os.getenv("IN_DOCKER", "false").lower() == "true"

    host = DB_HOST
    port = 5432 if any([ambiente_de_teste, em_docker]) else 5439
    password = DB_PASSWORD
    user = DB_USER
    db_name = DB_NAME
    database_uri = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{db_name}"

    return database_uri


# ---------- Database setup ----------
DATABASE_URL = obter_uri_do_banco_de_dados()
engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)
Base = declarative_base()


# ---------- Context managers ----------
@contextmanager
def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@contextmanager
def get_tenant_session(schema_id: str):
    with get_db_session() as db:
        # switch search_path to tenant schema
        db.execute(text(f'SET search_path TO "{schema_id}"'))
        yield db


def create_tenant_schema(schema_id: str):
    """
    1. Cria o schema no Postgres
    2. Ajusta os metadados para usar schema_id
    3. Cria as tabelas do tenant dentro dele
    4. Restaura schema=None nos metadados
    """
    # 1) criar schema
    with engine.begin() as conn:
        conn.execute(text(f'CREATE SCHEMA IF NOT EXISTS "{schema_id}"'))

    # 2) atribuir schema nos objetos
    for table in Base.metadata.sorted_tables:
        table.schema = schema_id

    # 3) criar tabelas no novo schema
    Base.metadata.create_all(bind=engine)

    # 4) restaurar esquema padrão (public)
    for table in Base.metadata.sorted_tables:
        table.schema = None


SCHEMAS_PARA_NAO_LISTAR: tuple[str, ...] = (
    "public",
    "information_schema",
    "pg_catalog",
    "pg_toast",
)


def listar_schemas_existentes() -> list[str]:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT schema_name FROM information_schema.schemata"))
        return [row[0] for row in result if row[0] not in SCHEMAS_PARA_NAO_LISTAR]


def verificar_schema_existente(schema_id: str) -> None:
    """
    Verifica se o schema existe no banco de dados.
    :param schema_id: ID do schema a ser verificado.
    :return: True se o schema existir, False caso contrário.
    """
    with engine.begin() as conn:
        result = conn.execute(
            text(
                f"SELECT schema_name FROM information_schema.schemata WHERE schema_name = '{schema_id}'"
            )
        )
        if result.fetchone():
            raise ValueError(f"Schema {schema_id} já existe")


def criar_primeira_empresa_e_usuario():
    from src.models import Empresa, Usuario

    schemas = listar_schemas_existentes()
    # verificar se algum schema é um uuid valido
    for schema in schemas:
        try:
            UUID(schema)
            return
        except ValueError:
            pass

    # gerar uuid
    id_empresa = uuid4()

    # verificar se ha schema com esse uuid
    verificar_schema_existente(str(id_empresa))

    # criar schema
    create_tenant_schema(str(id_empresa))

    # criar empresa
    with get_tenant_session(str(id_empresa)) as db:
        emp = Empresa(nome="Empresa 1", id=id_empresa)
        db.add(emp)
        db.commit()
        db.refresh(emp)

    # criar usuario
    with get_tenant_session(str(id_empresa)) as db:
        user = Usuario(
            email=EMAIL_PRIMEIRO_USUARIO,
            senha=SENHA_PRIMEIRO_USUARIO,
            empresa_id=id_empresa,
        )
        db.add(user)
        db.commit()
        db.refresh(user)
