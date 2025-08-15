export COMPOSE_NAME=banco_com_schemas

docker-clean:
	docker system prune -f

compose:
	docker-compose -f docker-compose.yml --env-file .env -p $(COMPOSE_NAME) up --build -d

ruff:
	ruff format . && ruff check . --fix

install:
	uv sync

activate:
	uv venv