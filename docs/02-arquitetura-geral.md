# 02 — Arquitetura Geral do ZeeK.Web

## 2.1 Visão Arquitetural

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (React)                      │
│  ┌──────────┐  ┌──────────┐  ┌──────────────────────┐   │
│  │Dashboard │  │  Pages   │  │ Configuradores       │   │
│  │(status,  │  │(trading, │  │(CUSTOM, Multiplicador│   │
│  │ saldo)   │  │ gráfico) │  │ Setup, Análise)      │   │
│  └────┬─────┘  └────┬─────┘  └──────────┬───────────┘   │
│       │             │                   │               │
│  ┌────▼─────────────▼───────────────────▼───────────┐   │
│  │            WebSocket Client (market/ticks)        │   │
│  │            REST Client (operações)                │   │
│  └───────────────────────┬───────────────────────────┘   │
└──────────────────────────┼───────────────────────────────┘
                           │ HTTP + WS
┌──────────────────────────┼───────────────────────────────┐
│                    BACKEND (FastAPI)                      │
│  ┌───────────────────────▼───────────────────────────┐   │
│  │              API Gateway (FastAPI)                  │   │
│  │  ┌─────────┐  ┌──────────┐  ┌────────────────┐    │   │
│  │  │ REST    │  │ WebSocket│  │ Auth/Security  │    │   │
│  │  │ Routes  │  │ Handler  │  │ (JWT, CORS)    │    │   │
│  │  └────┬────┘  └────┬─────┘  └────────────────┘    │   │
│  └───────┼────────────┼───────────────────────────────┘   │
│          │            │                                   │
│  ┌───────▼────────────▼───────────────────────────────┐   │
│  │                 Services                            │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│  │  │Deriv     │ │ Estratég.│ │ Gerenciamento    │    │   │
│  │  │Connector │ │ Motor    │ │ de Banca         │    │   │
│  │  │(WS+API)  │ │(CUSTOM, │ │(Martingale,      │    │   │
│  │  │          │ │ Gatilhos)│ │ Soros, Limites)  │    │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘    │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│  │  │Indicado.│ │ Análise  │ │ Licenciamento    │    │   │
│  │  │Técnicos │ │ Padrões  │ │ (validação)      │    │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Workers Async                          │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────────────┐    │   │
│  │  │Deriv     │ │ Heartbeat│ │ Watchdog         │    │   │
│  │  │Connector │ │ Monitor  │ │ Mercado          │    │   │
│  │  └──────────┘ └──────────┘ └──────────────────┘    │   │
│  └────────────────────────────────────────────────────┘   │
│                                                           │
│  ┌────────────────────────────────────────────────────┐   │
│  │              Database (SQLite/Postgres)             │   │
│  │  users | tokens | trades | strategies | setups     │   │
│  └────────────────────────────────────────────────────┘   │
└──────────────────────────────────────────────────────────┘
                           │
               ┌───────────▼───────────┐
               │   Deriv API (WS + REST)│
               │   wss://ws.derivws.com │
               │   api.derivws.com      │
               └───────────────────────┘
```

---

## 2.2 Decisões Arquiteturais

### Por que FastAPI + React?
- **FastAPI:** Suporte nativo a WebSocket, async/await, alta performance, auto-docs
- **React:** Ecossistema maduro, hooks para tempo real, TypeScript para segurança
- **WebSocket bidirecional:** Essencial para ticks em tempo real (igual ao original)

### Por que Workers separados?
- A conexão com a Deriv precisa ser **persistente** (WebSocket)
- Separar o worker de conexão da API REST evita bloqueios
- Permite múltiplas contas simultâneas (como o original faz com `DerivWorker` + `DerivMultiWorker`)

### Estrutura de Dados
- **Sessão de trading:** estado vivo em memória (não no banco)
- **Histórico:** persistido em SQLite/Postgres para consulta
- **Configurações:** JSON armazenado no banco (setups, preferências)

---

## 2.3 Fluxo de Dados (Operação)

```
1. Front-end envia POST /api/trade/start
   → Backend cria worker (thread)
   → Worker conecta na Deriv WS
   → Worker assina ticks do mercado

2. Deriv envia tick
   → Worker recebe tick
   → Worker avalia regras CUSTOM
   → Se gatilho ativo → envia proposal para Deriv
   → Deriv responde com proposal
   → Se aceito → envia buy
   → Deriv responde com contract_id

3. Resultado do contrato
   → Deriv envia transaction update
   → Worker processa win/loss
   → Aplica gestão de banca (Martingale, Soros)
   → Envia resultado para front-end via WS

4. Front-end atualiza:
   → Gráfico (novo tick)
   → Saldo (novo balance)
   → Histórico (nova ocorrência)
   → Status da página
```

---

## 2.4 Estados do Sistema

### Conexão com Deriv
```
DISCONNECTED → CONNECTING → AUTHORIZING → CONNECTED → TRADING
                    ↓            ↓
               RECONNECTING  ERROR (token inválido)
```

### Página de Operação
```
STOPPED → RUNNING (avaliando gatilhos)
   ↓          ↓
PAUSED   TRADING (contrato ativo)
   ↓          ↓
STOPPED   COMPLETED (win/loss)
```

### Defesa
```
SEM DEFESA
BARREIRA (só opera após X losses consecutivos)
SOROS MASTER (lidera operações)
SOROS SLAVE (segue MASTER com barreira própria)
```

---

## 2.5 Componentes do Backend

| Componente | Responsabilidade |
|-----------|-----------------|
| **DerivClient** | Conexão WebSocket com a Deriv, autenticação, subscribe |
| **StrategyEngine** | Avalia gatilhos CUSTOM, decide entrada |
| **OrderManager** | Envia proposals, monitora buy, processa resultados |
| **BankrollManager** | Gerencia stake, Martingale, limites, mini-meta |
| **DefenseSystem** | Aplica barreira/defesa |
| **IndicatorService** | Calcula SMA, EMA, RSI, MACD, Bollinger |
| **PatternAnalyzer** | Análise de padrões em ticks históricos |
| **LicenseValidator** | Valida licença local + remota |
| **MonitorService** | Heartbeat para servidor de monitoramento |
| **UserSession** | Gerencia sessão do usuário (JWT) |

---

## 2.6 Componentes do Frontend

| Componente | Descrição |
|-----------|-----------|
| **Dashboard** | Status geral, conexão, saldo, profit, ping |
| **OperationPage** | Página de trading com gráfico e controles |
| **TradeChart** | Gráfico de ticks com indicadores (Lightweight Charts) |
| **CustomStrategyBuilder** | Configurador visual de regras CUSTOM |
| **MartingaleConfig** | Configuração de Martingale/Multiplicador |
| **DefenseConfig** | Configuração de defesa (barreira, soros) |
| **SetupManager** | Salvar/carregar estratégias completas |
| **PatternAnalysis** | Ferramenta de análise de padrões |
| **LogViewer** | Visualizador de log do sistema |
| **TokenDialog** | Dialog de configuração do token PAT |
| **Calculator** | Calculadora de multiplicador |
| **MiniMetaDialog** | Dialog de mini-meta atingida |

---

## 2.7 Tecnologias Específicas

### Frontend
- **Vite** — Build tool rápida
- **TypeScript** — Tipagem segura
- **TailwindCSS** — Estilização utilitária
- **Lightweight Charts** — Gráfico de ticks pela TradingView
- **Zustand** — Estado global simples
- **React Router** — Navegação
- **Socket.io Client** — WebSocket (ou raw WebSocket)

### Backend
- **FastAPI** — Framework REST + WebSocket
- **SQLAlchemy** — ORM
- **Alembic** — Migrações
- **Celery** — Fila de tarefas (opcional)
- **Redis** — Cache + fila
- **Pydantic** — Validação
- **JWT** — Autenticação
- **Websockets** — Conexão com Deriv

---

## 2.8 Segurança

- **Tokens PAT:** Armazenados criptografados no banco (hash + salt)
- **JWT:** Sessão do usuário com expiry
- **CORS:** Restrito ao domínio do frontend
- **HTTPS:** Obrigatório em produção
- **Rate Limiting:** Previne abuso da API
- **Validação de Licença:** Vinculada a email + machine_id (herdado do original)
