from __future__ import annotations

from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, String, LargeBinary, Index
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.banco_de_dados import Base


class Usuario(Base):
    __tablename__ = "usuario"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    empresa_id: Mapped[UUID] = mapped_column(ForeignKey("empresa.id"), nullable=False)
    email: Mapped[str] = mapped_column(
        String(255), nullable=False, unique=True, index=True
    )
    senha: Mapped[str] = mapped_column(String(255), nullable=False)
    # relacoes
    empresa = relationship(
        "Empresa",
        back_populates="usuarios",
        foreign_keys=[empresa_id],
    )


class UsuariosPublicos(Base):
    __tablename__ = "usuarios"
    __table_args__ = (
        Index("ix_usuarios_email_enc_empresa", "email_enc", "empresa_id"),
        {"schema": "public"},
    )

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    email_hash: Mapped[str] = mapped_column(
        String(64), nullable=False, unique=True, index=True
    )
    email_enc: Mapped[bytes] = mapped_column(LargeBinary, nullable=False)
    empresa_id: Mapped[UUID] = mapped_column(UUID, nullable=False)
    password_hash: Mapped[str] = mapped_column(String(128), nullable=False)


class Empresa(Base):
    __tablename__ = "empresa"

    id: Mapped[UUID] = mapped_column(UUID, primary_key=True, unique=True, default=uuid4)
    nome: Mapped[str] = mapped_column(String(255), nullable=False, unique=True)
    # relacoes
    usuarios = relationship(
        "Usuario",
        back_populates="empresa",
        foreign_keys=[Usuario.empresa_id],
    )
