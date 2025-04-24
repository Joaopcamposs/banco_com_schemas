from __future__ import annotations

from pydantic import BaseModel, UUID4


class CadastrarEmpresaSchema(BaseModel):
    nome: str


class LerEmpresaSchema(BaseModel):
    id: UUID4
    nome: str


class CadastrarUsuarioSchema(BaseModel):
    email: str
    senha: str
    empresa_id: UUID4


class LerUsuarioSchema(BaseModel):
    id: UUID4
    email: str
    empresa_id: UUID4


class Token(BaseModel):
    access_token: str
    token_type: str


class TokenData(BaseModel):
    username: str | None = None
    scopes: list[str] = []
