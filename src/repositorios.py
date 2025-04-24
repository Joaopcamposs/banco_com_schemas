from uuid import UUID, uuid4

from sqlalchemy import select

from src.banco_de_dados import (
    create_tenant_schema,
    get_tenant_session,
)
from src.executores import hash_email, decrypt_email, encrypt_email, hash_password
from src.models import Usuario, Empresa, UsuariosPublicos


class CompanyRepository:
    def list(self, schema_id: str) -> list[Empresa]:
        with get_tenant_session(schema_id) as db:
            empresas = db.query(Empresa).all()
            return empresas

    def create(self, name: str, id_empresa: UUID | None = None) -> Empresa:
        # cria schema e tabelas
        id_empresa = id_empresa or uuid4()

        create_tenant_schema(str(id_empresa))
        with get_tenant_session(str(id_empresa)) as db:
            emp = Empresa(nome=name, id=id_empresa)
            db.add(emp)
            db.commit()
            db.refresh(emp)
            return emp


class UserRepository:
    def list(self, empresa_id: UUID) -> list[Usuario]:
        with get_tenant_session(str(empresa_id)) as db:
            usuarios = db.query(Usuario).all()
            return usuarios

    def get_user_by_email_and_empresa_id(
        self, email: str, empresa_id: UUID
    ) -> Usuario | None:
        with get_tenant_session(str(empresa_id)) as db:
            usuario = (
                db.execute(select(Usuario).where(Usuario.email == email))
                .scalars()
                .first()
            )
            return usuario

    def get_public_user_by_email(self, email: str) -> UsuariosPublicos | None:
        ehash = hash_email(email)
        with get_tenant_session("public") as db:
            stmt = select(UsuariosPublicos).where(UsuariosPublicos.email_hash == ehash)
            user = db.execute(stmt).scalars().first()
        if user and decrypt_email(user.email_enc) == email:
            return user
        return None

    def create(self, email: str, senha: str, empresa_id: UUID) -> Usuario:
        with get_tenant_session(str(empresa_id)) as db:
            usr = Usuario(email=email, senha=hash_password(senha), empresa_id=empresa_id)
            db.add(usr)
            db.commit()
            db.refresh(usr)

        self.create_public_user(email, senha, empresa_id)

        return usr

    def create_public_user(self, email: str, raw_password: str, empresa_id: UUID):
        ehash = hash_email(email)
        # já criptografa email e gera hash
        email_enc = encrypt_email(email)
        pwd_hash = hash_password(
            raw_password
        )  # sua função de hash de senha (bcrypt, argon2...)
        user = UsuariosPublicos(
            email_hash=ehash,
            email_enc=email_enc,
            password_hash=pwd_hash,
            empresa_id=empresa_id,
        )
        with get_tenant_session("public") as db:
            db.add(user)
            db.commit()
            db.refresh(user)
        return user
