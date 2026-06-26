---
name: zeek-web-rebuild
title: "ZeeK.Web — Bot de Trading Deriv"
description: "Reconstrução do ZeeK.Bot 3.1 (bot Deriv CALL/PUT) em FastAPI + React. 11 docs, 7 fases de implementação, scaffold completo."
triggers:
  - "zeek"
  - "zeek.bot"
  - "ZeeK"
  - "bot deriv"
  - "trading bot"
  - "ZeeK.Web"
---

## Contexto

Projeto de reconstrução do **ZeeK.Bot 3.1** (bot de opções binárias CALL/PUT para a plataforma Deriv) em versão web: **FastAPI + React + WebSocket**.

ZeeK.Bot original: Python 3.13 + Nuitka (compilado pra C++ nativo) + PySide6.  
Informações extraídas do binário por engenharia reversa.

## Stack

- Backend: FastAPI + WebSockets + SQLAlchemy + Redis
- Frontend: React 18 + TypeScript + TailwindCSS + Lightweight Charts
- Infra: Docker Compose

## Deriv

- WebSocket: `wss://ws.derivws.com/websockets/v3?app_id=24332`
- API REST: `https://api.derivws.com`
- Mercados: R_100, R_75, R_50, R_25, R_10, 1HZ

## Docs (ordem pra ler)

| Arquivo | Conteúdo |
|---------|----------|
| docs/00-resumo-executivo.md | Visão geral |
| docs/01-analise-do-zeek-original.md | Eng. reversa completa |
| docs/02-arquitetura-geral.md | Diagramas, fluxos |
| docs/03-api-deriv-integracao.md | WS Deriv + código |
| docs/04-estrategias-e-logica.md | CUSTOM, indicadores, defesas |
| docs/05-estrutura-do-projeto.md | Arquivo por arquivo |
| docs/06-plano-de-implementacao.md | 7 fases, ~34 dias |
| docs/07-frontend-react.md | Componentes, temas |
| docs/08-backend-fastapi.md | Rotas, modelos |
| docs/09-deploy-e-infra.md | Docker, produção |
| docs/10-glossario.md | Termos |

## Serviços já codificados

- `backend/app/services/deriv_client.py` — WS Deriv completo
- `backend/app/services/indicators.py` — SMA, EMA, RSI, MACD, BB
- `backend/app/services/strategy_engine.py` — Regras CUSTOM
- `backend/app/services/bankroll.py` — Banca + Martingale
- `backend/app/services/defense.py` — Barreira, Soros
- `backend/app/services/page_manager.py` — Multi-páginas
- Models SQLAlchemy, auth JWT, Dockerfiles

## Início rápido

```bash
bash scripts/setup-dev.sh  # ou manual: pip install -r requirements.txt + npm install
make dev                   # Docker: backend + frontend + redis
```

Acessos:
- Frontend: http://localhost:5173
- Backend: http://localhost:8000
- Swagger: http://localhost:8000/docs

## Criador do ZeeK original

Lukas Martins — zeekbot2020@gmail.com — zeek.bot — @zeekbot4020  
Licença: servidor remoto 79.143.190.252:8765

## Notas

- App ID 24332 é do ZeeK original. Criar próprio em https://app.deriv.com/account/api-token
- ZeeK.Bot original não é open source — engenharia reversa para aprendizado
- Projeto verificado: 24 arquivos .py OK, 30+ arquivos essenciais presentes
