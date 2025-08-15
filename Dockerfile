FROM python:3.11-slim

# Cria diretório da app
WORKDIR /banco_com_schemas

# Instalações básicas
RUN apt-get update && apt-get install -y curl build-essential

# Copia a aplicação
COPY . .

# Instala dependências
RUN pip install --upgrade pip
RUN pip install uv
RUN uv sync

# Adiciona o .venv/bin ao PATH do container
ENV PATH="/banco_com_schemas/.venv/bin:$PATH"

# Comando padrão
CMD ["uvicorn", "src.api:app", "--host", "0.0.0.0", "--port", "8000"]
