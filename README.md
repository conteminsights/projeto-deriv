# ZeeK.Web — Bot de Trading para Deriv (Versão Web)

[![GitHub](https://img.shields.io/badge/GitHub-conteminsights%2Fprojeto--deriv-f86525?style=flat&logo=github)](https://github.com/conteminsights/projeto-deriv)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-009688?style=flat&logo=fastapi)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/React-18.3-61DAFB?style=flat&logo=react)](https://react.dev/)
[![License](https://img.shields.io/badge/License-Proprietary-ffd64f?style=flat)]()

Recriação completa do **ZeeK.Bot 3.1** (bot de opções binárias para a plataforma **Deriv**) em arquitetura web moderna:
**FastAPI + React + WebSocket**.

> **Status:** 🟢 Versão 1.0 — Funcionalmente equivalente ao ZeeK 3.1  
> **Versão alvo:** 1.0 (funcionalmente equivalente ao ZeeK 3.1)

---

## Visão Geral

O ZeeK.Bot original é um bot de trading desktop para a Deriv que:
- Opera nos mercados sintéticos (R_100, R_75, R_50, R_25, R_10, 1HZ...)
- Executa estratégias **CUSTOM** com gatilhos baseados em indicadores técnicos
- Suporta **Martingale**, **Soros (MASTER/SLAVE)**, **Multiplicador**
- Gerencia banca com mini-meta, mxm entradas, limites globais
- Análise de padrões e indicadores em tempo real

Esta versão web recria **todas as funcionalidades** em uma stack moderna.

---

## Stack Tecnológica

| Camada | Tecnologia |
|--------|-----------|
| **Backend** | Python 3.12+, FastAPI, WebSockets, Uvicorn |
| **Frontend** | React 18+ (Vite), TypeScript, TailwindCSS |
| **Tempo Real** | WebSocket bidirecional |
| **Banco** | SQLite (dev) / PostgreSQL (prod) |
| **Fila** | Celery + Redis (para workers assíncronos) |
| **Deploy** | Docker Compose |

---

## Estrutura do Projeto

```
zeek-web/
├── docs/                          # Documentação completa
│   ├── 00-resumo-executivo.md     # Este documento
│   ├── 01-analise-do-zeek-original.md
│   ├── 02-arquitetura-geral.md
│   ├── 03-api-deriv-integracao.md
│   ├── 04-estrategias-e-logica.md
│   ├── 05-estrutura-do-projeto.md
│   ├── 06-plano-de-implementacao.md
│   ├── 07-frontend-react.md
│   ├── 08-backend-fastapi.md
│   ├── 09-deploy-e-infra.md
│   └── 10-glossario.md
├── backend/                       # API FastAPI
│   ├── app/
│   │   ├── api/                   # Rotas REST + WebSocket
│   │   ├── core/                  # Config, segurança, db
│   │   ├── models/                # Modelos Pydantic / SQLAlchemy
│   │   ├── services/              # Lógica de negócio
│   │   └── workers/               # Workers assíncronos
│   ├── tests/
│   ├── requirements.txt
│   └── Dockerfile
├── frontend/                      # SPA React
│   ├── src/
│   │   ├── components/            # Componentes reutilizáveis
│   │   ├── pages/                 # Páginas
│   │   ├── hooks/                 # Hooks customizados
│   │   ├── services/              # API + WebSocket clients
│   │   ├── store/                 # Estado global (Zustand)
│   │   └── types/                 # TypeScript types
│   ├── package.json
│   └── Dockerfile
├── scripts/                       # Scripts auxiliares
│   ├── setup-dev.sh
│   └── seed-data.py
├── docker-compose.yml
└── Makefile
```

---

## Começando

### Pré-requisitos
- Python 3.12+
- Node.js 20+
- Docker + Docker Compose (opcional)

### Desenvolvimento

```bash
# Backend
cd backend
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend
cd frontend
npm install
npm run dev
```

Acesse:
- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- Docs Swagger: http://localhost:8000/docs

---

## Documentação

Veja a pasta `docs/` para documentação detalhada:

1. **[Resumo Executivo](docs/00-resumo-executivo.md)** — visão geral do projeto
2. **[Análise do ZeeK Original](docs/01-analise-do-zeek-original.md)** — tudo que foi extraído do binário
3. **[Arquitetura Geral](docs/02-arquitetura-geral.md)** — diagramas e decisões técnicas
4. **[API Deriv](docs/03-api-deriv-integracao.md)** — conexão WebSocket, autenticação, endpoints
5. **[Estratégias](docs/04-estrategias-e-logica.md)** — CUSTOM, Martingale, Soros, regras e gatilhos
6. **[Estrutura do Projeto](docs/05-estrutura-do-projeto.md)** — cada arquivo explicado
7. **[Plano de Implementação](docs/06-plano-de-implementacao.md)** — fases, tarefas, estimativas
8. **[Frontend React](docs/07-frontend-react.md)** — componentes, estados, fluxos
9. **[Backend FastAPI](docs/08-backend-fastapi.md)** — rotas, workers, websockets
10. **[Deploy e Infra](docs/09-deploy-e-infra.md)** — Docker, produção, monitoramento
11. **[Glossário](docs/10-glossario.md)** — termos técnicos

---

## Fases de Implementação

| Fase | Descrição | Duração |
|------|-----------|---------|
| **1** | Fundação: Backend core + conexão Deriv | 3-4 dias |
| **2** | Motor de trading: ordens, contratos, WebSocket | 4-5 dias |
| **3** | Estratégias: CUSTOM, gatilhos, indicadores | 5-7 dias |
| **4** | Gestão de banca: Martingale, Soros, limites | 3-4 dias |
| **5** | Frontend: dashboard, configurador, gráficos | 5-7 dias |
| **6** | UI completa: páginas, análise, setups | 4-5 dias |
| **7** | Testes, deploy, documentação final | 3-4 dias |

**Total estimado:** 27-36 dias (1 dev full-time)

---

## Licenciamento

Este projeto é uma engenharia reversa para fins de aprendizado e recriação independente.
O ZeeK.Bot original é de propriedade de Lukas Martins / ZeeK (zeek.bot).
