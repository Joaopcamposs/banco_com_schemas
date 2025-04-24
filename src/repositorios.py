from uuid import UUID, uuid4

from src.banco_de_dados import (
    create_tenant_schema,
    get_tenant_session,
)
from src.models import Usuario, Empresa


class CompanyRepository:
    def list(self, schema_id: str) -> list[Empresa]:
        with get_tenant_session(schema_id) as db:
            empresas = db.query(Empresa).all()
            return empresas

    def create(self, name: str) -> Empresa:
        # cria schema e tabelas
        id_empresa = uuid4()

        create_tenant_schema(str(id_empresa))
        with get_tenant_session(str(id_empresa)) as db:
            emp = Empresa(nome=name, id=id_empresa)
            db.add(emp)
            db.commit()
            db.refresh(emp)
            return emp


class UserRepository:
    def list(self, schema_id: str) -> list[Usuario]:
        with get_tenant_session(schema_id) as db:
            usuarios = db.query(Usuario).all()
            return usuarios

    def create(self, email: str, senha: str, empresa_id: UUID) -> Usuario:
        with get_tenant_session(str(empresa_id)) as db:
            usr = Usuario(email=email, senha=senha, empresa_id=empresa_id)
            db.add(usr)
            db.commit()
            db.refresh(usr)
            return usr
