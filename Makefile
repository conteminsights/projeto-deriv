.PHONY: dev build test clean

# Development
dev:
	docker compose up --build

dev-backend:
	cd backend && uvicorn app.main:app --reload

dev-frontend:
	cd frontend && npm run dev

# Build
build:
	docker compose build

# Test
test:
	cd backend && python -m pytest
	cd frontend && npm test

# Clean
clean:
	docker compose down -v
	rm -rf backend/__pycache__ backend/**/__pycache__
	rm -rf frontend/node_modules frontend/dist

# Database
migrate:
	cd backend && alembic upgrade head

migration:
	cd backend && alembic revision --autogenerate -m "$(name)"

# Setup
setup:
	cd backend && python -m venv .venv && . .venv/bin/activate && pip install -r requirements.txt
	cd frontend && npm install

# Help
help:
	@echo "ZeeK.Web — Comandos"
	@echo ""
	@echo "  make dev          — Sobe tudo com Docker"
	@echo "  make dev-backend  — Backend apenas (hot reload)"
	@echo "  make dev-frontend — Frontend apenas (hot reload)"
	@echo "  make build        — Build das imagens Docker"
	@echo "  make test         — Roda testes"
	@echo "  make setup        — Setup inicial do ambiente"
	@echo "  make clean        — Limpa tudo"
