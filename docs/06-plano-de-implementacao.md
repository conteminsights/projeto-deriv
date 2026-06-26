# 06 — Plano de Implementação

> Duração estimada: 27-36 dias (1 dev full-time)

---

## Fase 1: Fundação (Dias 1-4)

### Objetivo
Backend funcional com conexão Deriv e estrutura base.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 1.1 | Criar projeto FastAPI com estrutura de pastas | `backend/` | 2h |
| 1.2 | Configurar banco SQLite + SQLAlchemy + Alembic | `backend/app/core/database.py` | 3h |
| 1.3 | Modelos de dados (User, Token, Trade, Setup) | `backend/app/models/` | 4h |
| 1.4 | DerivClient: conexão WebSocket básica | `backend/app/services/deriv_client.py` | 6h |
| 1.5 | Autenticação JWT + login | `backend/app/core/auth.py` | 4h |
| 1.6 | API de autenticação (register, login, logout) | `backend/app/api/auth.py` | 3h |
| 1.7 | API de token PAT (CRUD criptografado) | `backend/app/api/tokens.py` | 3h |
| 1.8 | Testes da Fase 1 | `backend/tests/` | 3h |

### Marcos
- [x] Servidor FastAPI rodando
- [x] Conexão WebSocket com a Deriv estabelecida
- [x] Usuário consegue salvar token e autenticar

---

## Fase 2: Motor de Trading (Dias 5-9)

### Objetivo
Conexão com a Deriv funcional: ticks, proposals, compra e venda.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 2.1 | DerivClient: subscribe ticks + balance | `backend/app/services/deriv_client.py` | 6h |
| 2.2 | DerivClient: proposal + buy + monitor | `backend/app/services/deriv_client.py` | 6h |
| 2.3 | Worker de conexão Deriv (background) | `backend/app/workers/deriv_worker.py` | 4h |
| 2.4 | Gerenciador de mercado (subscribe/switch) | `backend/app/services/market_manager.py` | 3h |
| 2.5 | Modelo de contrato/trade no banco | `backend/app/models/trade.py` | 2h |
| 2.6 | WebSocket handler para frontend | `backend/app/api/ws.py` | 4h |
| 2.7 | API de status (conexão, saldo, mercados) | `backend/app/api/status.py` | 3h |
| 2.8 | Testes de conexão e WebSocket | `backend/tests/` | 4h |

### Marcos
- [x] Ticks chegando em tempo real no backend
- [x] Proposals sendo solicitadas
- [x] Contratos sendo comprados via API
- [x] Frontend recebe ticks via WebSocket

---

## Fase 3: Estratégia CUSTOM (Dias 10-17)

### Objetivo
Motor completo de estratégia CUSTOM com indicadores e gatilhos.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 3.1 | Calculadora de indicadores (SMA, EMA) | `backend/app/services/indicators.py` | 4h |
| 3.2 | Calculadora de indicadores (RSI, MACD, BB) | `backend/app/services/indicators.py` | 4h |
| 3.3 | Avaliador de condições/regras | `backend/app/services/rule_engine.py` | 6h |
| 3.4 | StrategyEngine: avaliação a cada tick | `backend/app/services/strategy_engine.py` | 8h |
| 3.5 | OrderManager: execução de ordens | `backend/app/services/order_manager.py` | 6h |
| 3.6 | Modelos de estratégia (pydantic) | `backend/app/models/strategy.py` | 3h |
| 3.7 | API de estratégias (CRUD) | `backend/app/api/strategies.py` | 4h |
| 3.8 | Operação multi-página | `backend/app/services/page_manager.py` | 4h |
| 3.9 | Testes de lógica CUSTOM | `backend/tests/` | 6h |

### Marcos
- [x] Estratégia CUSTOM executando com gatilhos
- [x] Múltiplas páginas operando simultaneamente
- [x] Indicadores calculados corretamente
- [x] Ordens executadas baseadas em regras

---

## Fase 4: Gestão de Banca (Dias 18-21)

### Objetivo
Martingale, Soros, mini-meta, limites e defesas.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 4.1 | BankrollManager: stake, Martingale | `backend/app/services/bankroll.py` | 6h |
| 4.2 | DefenseSystem: barreira, modos | `backend/app/services/defense.py` | 4h |
| 4.3 | Sistema Soros (MASTER/SLAVE) | `backend/app/services/soros.py` | 8h |
| 4.4 | Mini-meta + mxm entradas | `backend/app/services/mini_meta.py` | 4h |
| 4.5 | Limites globais de lucro/prejuízo | `backend/app/services/limits.py` | 3h |
| 4.6 | Auto-reload e reset controlado | `backend/app/services/auto_reload.py` | 4h |
| 4.7 | API de configuração de banca | `backend/app/api/bankroll.py` | 3h |
| 4.8 | Testes de gestão de banca | `backend/tests/` | 4h |

### Marcos
- [x] Martingale progressivo funcional
- [x] Soros MASTER/SLAVE operando
- [x] Mini-meta disparando reset
- [x] Limites globais respeitados

---

## Fase 5: Frontend — Core (Dias 22-28)

### Objetivo
Interface web funcional com dashboard, gráficos e configuradores.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 5.1 | Setup Vite + React + Tailwind + Router | `frontend/` | 2h |
| 5.2 | Tipos TypeScript (compartilhados) | `frontend/src/types/` | 3h |
| 5.3 | Serviço WebSocket + REST API client | `frontend/src/services/` | 4h |
| 5.4 | Store global (Zustand) | `frontend/src/store/` | 3h |
| 5.5 | Página de Login + token config | `frontend/src/pages/Login.tsx` | 4h |
| 5.6 | Dashboard principal (status, saldo) | `frontend/src/pages/Dashboard.tsx` | 6h |
| 5.7 | OperationPage (gráfico + controles) | `frontend/src/pages/OperationPage.tsx` | 8h |
| 5.8 | Gráfico de ticks (Lightweight Charts) | `frontend/src/components/TradeChart.tsx` | 6h |
| 5.9 | Indicadores no gráfico (SMA, BB, RSI) | `frontend/src/components/IndicatorOverlay.tsx` | 4h |
| 5.10 | WebSocket hook personalizado | `frontend/src/hooks/useDerivWS.ts` | 3h |

### Marcos
- [x] Tela de login funcional
- [x] Dashboard mostrando saldo e status
- [x] Gráfico de ticks em tempo real
- [x] Página de operação com controles básicos

---

## Fase 6: Frontend — Completo (Dias 29-33)

### Objetivo
Todas as telas e funcionalidades do ZeeK originais.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 6.1 | Configurador CUSTOM (regras visuais) | `frontend/src/components/CustomStrategyBuilder.tsx` | 8h |
| 6.2 | Configuração de Martingale/Multiplicador | `frontend/src/components/MartingaleConfig.tsx` | 3h |
| 6.3 | Configuração de defesa (barreira, soros) | `frontend/src/components/DefenseConfig.tsx` | 4h |
| 6.4 | Gerenciador de setups (salvar/carregar) | `frontend/src/pages/SetupManager.tsx` | 6h |
| 6.5 | Análise de padrões | `frontend/src/pages/PatternAnalysis.tsx` | 6h |
| 6.6 | Log do sistema + compactação | `frontend/src/components/LogViewer.tsx` | 3h |
| 6.7 | Calculadora de multiplicador | `frontend/src/components/Calculator.tsx` | 3h |
| 6.8 | Mini-meta dialog + mxm entradas | `frontend/src/components/MiniMetaDialog.tsx` | 3h |
| 6.9 | Modo escuro + tema consistente | `frontend/src/theme.ts` | 2h |
| 6.10 | Responsividade e ajustes finos | Vários | 4h |

### Marcos
- [x] Configurador CUSTOM funcional (add/remove/edit regras)
- [x] Setups salvando e carregando
- [x] Análise de padrões com resultados
- [x] Todas as telas do ZeeK implementadas

---

## Fase 7: Finalização (Dias 34-38)

### Objetivo
Testes, documentação, Docker, deploy.

### Tarefas

| # | Tarefa | Arquivos | Estimativa |
|---|--------|----------|------------|
| 7.1 | Testes de integração backend | `backend/tests/` | 6h |
| 7.2 | Testes de frontend (vitest) | `frontend/src/*.test.ts` | 4h |
| 7.3 | Docker Compose (backend + frontend + redis) | `docker-compose.yml` | 3h |
| 7.4 | Dockerfiles otimizados | `backend/Dockerfile`, `frontend/Dockerfile` | 3h |
| 7.5 | Documentação de deploy | `docs/09-deploy-e-infra.md` | 2h |
| 7.6 | README final + badges | `README.md` | 1h |
| 7.7 | Correção de bugs e polish | Vários | 8h |

### Marcos
- [x] Testes passando
- [x] Docker rodando localmente
- [x] Documentação completa
- [x] Pronto para deploy

---

## Resumo de Estimativas

| Fase | Horas | Dias |
|------|-------|------|
| 1 — Fundação | 28h | 4 |
| 2 — Motor de Trading | 32h | 5 |
| 3 — Estratégia CUSTOM | 41h | 7 |
| 4 — Gestão de Banca | 36h | 4 |
| 5 — Frontend Core | 39h | 5 |
| 6 — Frontend Completo | 38h | 5 |
| 7 — Finalização | 27h | 4 |
| **Total** | **~241h** | **~34 dias** |

---

## Dependências entre Fases

```
Fase 1 (Fundação)
    ↓
Fase 2 (Motor Trading) ←─── Pode começar após Fase 1
    ↓
Fase 3 (Estratégia CUSTOM) ←── Precisa da Fase 2
    ↓
Fase 4 (Gestão de Banca) ←── Precisa da Fase 3
    ↓
Fase 5 (Frontend Core) ←── Pode começar após Fase 2
    ↓
Fase 6 (Frontend Completo) ←── Precisa das Fases 3-4
    ↓
Fase 7 (Finalização)
```

### Paralelismo Possível
- **Fase 5** (Frontend Core) pode começar assim que **Fase 2** estiver estável
- A pessoa do frontend e do backend podem trabalhar em paralelo
- Fases 3 e 4 são sequenciais (backend puro)
