from __future__ import annotations

from uuid import uuid4

from sqlalchemy import UUID, ForeignKey, String
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
