FROM python:3.11-slim

# Cria diretório da app
WORKDIR /banco_com_schemas

# Instalações básicas
RUN apt-get update && apt-get install -y curl build-essential

# Instala o Poetry
ENV POETRY_VERSION=1.8.2
RUN curl -sSL https://install.python-poetry.org | python3 -
ENV PATH="/root/.local/bin:$PATH"

# Define o Poetry para criar o virtualenv dentro do projeto
RUN poetry config virtualenvs.in-project true

# Copia arquivos de dependência primeiro (melhora cache)
COPY pyproject.toml ./

# Instala dependências
RUN poetry lock && poetry install --no-root

# Adiciona o .venv/bin ao PATH do container
ENV PATH="/banco_com_schemas/.venv/bin:$PATH"

# Copia o restante da aplicação
COPY . .

# Comando padrão
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
