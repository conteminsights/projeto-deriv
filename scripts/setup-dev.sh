#!/bin/bash
# ZeeK.Web — Setup Script
# Uso: bash scripts/setup-dev.sh

set -e

echo "╔════════════════════════════════════════╗"
echo "║       ZeeK.Web — Setup Dev            ║"
echo "╚════════════════════════════════════════╝"

# Backend
echo ""
echo "📦 Configurando Backend..."
cd backend

if [ ! -d ".venv" ]; then
    python -m venv .venv
    echo "  ✓ Virtualenv criado"
fi

source .venv/bin/activate || source .venv/Scripts/activate
pip install -q -r requirements.txt
echo "  ✓ Dependências instaladas"

if [ ! -f ".env" ]; then
    cp .env.example .env
    echo "  ✓ .env criado (ajuste as variáveis)"
fi

cd ..

# Frontend
echo ""
echo "🎨 Configurando Frontend..."
cd frontend

if [ ! -d "node_modules" ]; then
    npm install
    echo "  ✓ Dependências instaladas"
fi

cd ..

# Done
echo ""
echo "✅ Setup concluído!"
echo ""
echo "Para iniciar:"
echo "  make dev           # Docker (recomendado)"
echo "  make dev-backend   # Backend apenas"
echo "  make dev-frontend  # Frontend apenas"
echo ""
echo "Acesse:"
echo "  Frontend: http://localhost:5173"
echo "  Backend:  http://localhost:8000"
echo "  Swagger:  http://localhost:8000/docs"
