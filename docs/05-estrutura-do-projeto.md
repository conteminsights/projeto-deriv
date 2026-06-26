# 05 — Estrutura do Projeto (Arquivo por Arquivo)

```
zeek-web/
├── README.md                           ← Este arquivo. Visão geral do projeto.
│
├── .gitignore                          ← Arquivos ignorados pelo Git.
├── .env                                ← Variáveis de ambiente (NÃO versionar).
├── docker-compose.yml                  ← Orquestração dos serviços (dev).
├── Makefile                            ← Comandos úteis (dev, build, test).
│
├── docs/                               ← Documentação completa (10 arquivos)
│   ├── 00-resumo-executivo.md          ← Resumo de 1 página
│   ├── 01-analise-do-zeek-original.md  ← Eng. reversa completa do ZeeK.Bot
│   ├── 02-arquitetura-geral.md         ← Diagramas, fluxos, componentes
│   ├── 03-api-deriv-integracao.md      ← WebSocket Deriv, mensagens, endpoints
│   ├── 04-estrategias-e-logica.md      ← CUSTOM, Martingale, Soros, indicadores
│   ├── 05-estrutura-do-projeto.md      ← Este arquivo
│   ├── 06-plano-de-implementacao.md    ← 7 fases, tarefas, estimativas
│   ├── 07-frontend-react.md            ← Componentes, estados, temas
│   ├── 08-backend-fastapi.md           ← Rotas, workers, modelos
│   ├── 09-deploy-e-infra.md            ← Docker, produção, monitoramento
│   └── 10-glossario.md                 ← Termos técnicos
│
├── backend/                            ← API FastAPI
│   ├── .env.example                    ← Exemplo de configuração
│   ├── requirements.txt                ← Dependências Python
│   ├── Dockerfile                      ← Imagem Docker (dev)
│   ├── Dockerfile.prod                 ← Imagem Docker (prod, multi-stage)
│   │
│   ├── app/
│   │   ├── __init__.py
│   │   ├── main.py                     ← Entrypoint FastAPI + lifespan
│   │   ├── config.py                   ← Config via pydantic-settings
│   │   │
│   │   ├── api/                        ← Rotas REST + WebSocket
│   │   │   ├── __init__.py
│   │   │   ├── router.py               ← Agrega todos os routers
│   │   │   ├── auth.py                 ← POST /auth/register, /auth/login
│   │   │   ├── tokens.py               ← CRUD tokens PAT Deriv
│   │   │   ├── status.py               ← GET /status, /status/accounts
│   │   │   ├── strategies.py           ← CRUD estratégias CUSTOM
│   │   │   ├── bankroll.py             ← GET/PUT /bankroll
│   │   │   ├── trades.py               ← GET /trades (histórico)
│   │   │   ├── setups.py               ← CRUD setups
│   │   │   └── ws.py                   ← WebSocket /ws (tempo real)
│   │   │
│   │   ├── core/                       ← Infraestrutura
│   │   │   ├── __init__.py
│   │   │   ├── database.py             ← SQLAlchemy engine + session
│   │   │   ├── security.py             ← JWT, bcrypt, criptografia
│   │   │   └── exceptions.py           ← Error handlers
│   │   │
│   │   ├── models/                     ← SQLAlchemy ORM models
│   │   │   ├── __init__.py
│   │   │   ├── user.py                 ← User (email, senha)
│   │   │   ├── token.py                ← DerivToken (PAT criptografado)
│   │   │   ├── trade.py                ← Trade (histórico de contratos)
│   │   │   └── setup.py                ← Setup (configurações salvas)
│   │   │
│   │   ├── schemas/                    ← Pydantic schemas
│   │   │   ├── __init__.py
│   │   │   ├── auth.py                 ← Auth schemas
│   │   │   ├── trade.py                ← Trade schemas
│   │   │   └── strategy.py             ← Strategy schemas
│   │   │
│   │   ├── services/                   ← Lógica de negócio
│   │   │   ├── __init__.py
│   │   │   ├── deriv_client.py         ← WebSocket Deriv client
│   │   │   ├── market_manager.py       ← Gerencia mercados
│   │   │   ├── strategy_engine.py      ← Avalia regras CUSTOM
│   │   │   ├── rule_engine.py          ← Avalia condições/gatilhos
│   │   │   ├── order_manager.py        ← Envia ordens
│   │   │   ├── indicators.py           ← SMA, EMA, RSI, MACD, BB
│   │   │   ├── bankroll.py             ← Stake, Martingale
│   │   │   ├── defense.py              ← Barreira, Soros
│   │   │   ├── soros.py                ← MASTER/SLAVE
│   │   │   ├── page_manager.py         ← Multi-páginas
│   │   │   ├── pattern_analyzer.py     ← Análise de padrões
│   │   │   └── license.py              ← Validação de licença
│   │   │
│   │   └── workers/                    ← Workers assíncronos
│   │       ├── __init__.py
│   │       ├── deriv_worker.py         ← Worker de conexão Deriv
│   │       └── monitor.py              ← Heartbeat monitor
│   │
│   ├── tests/                          ← Testes
│   │   ├── __init__.py
│   │   ├── conftest.py                 ← Fixtures
│   │   ├── test_auth.py
│   │   ├── test_deriv_client.py
│   │   ├── test_strategy.py
│   │   ├── test_indicators.py
│   │   └── test_bankroll.py
│   │
│   └── alembic/                        ← Migrações
│       └── versions/
│
├── frontend/                           ← SPA React
│   ├── package.json                    ← Dependências e scripts
│   ├── tsconfig.json                   ← Config TypeScript
│   ├── vite.config.ts                  ← Config Vite + proxy
│   ├── tailwind.config.js              ← Tema dark ZeeK
│   ├── postcss.config.js               ← PostCSS
│   ├── index.html                      ← HTML entrypoint
│   ├── Dockerfile.dev                  ← Imagem Docker (dev)
│   ├── Dockerfile                      ← Imagem Docker (prod)
│   └── nginx.conf                      ← Nginx para produção
│   │
│   └── src/
│       ├── main.tsx                    ← Entrypoint React
│       ├── App.tsx                     ← Router principal
│       ├── index.css                   ← Tailwind + estilos globais
│       ├── vite-env.d.ts
│       │
│       ├── types/                      ← Tipos TypeScript
│       │   ├── deriv.ts                ← Tipos da API Deriv
│       │   ├── strategy.ts             ← Estratégias e regras
│       │   ├── trade.ts                ← Contratos e trades
│       │   └── user.ts                 ← Usuário e auth
│       │
│       ├── services/                   ← Serviços
│       │   ├── api.ts                  ← REST client (axios)
│       │   ├── ws.ts                   ← WebSocket client
│       │   └── deriv.ts                ← Helpers Deriv
│       │
│       ├── store/                      ← Estado global (Zustand)
│       │   ├── authStore.ts
│       │   ├── derivStore.ts
│       │   ├── strategyStore.ts
│       │   └── uiStore.ts
│       │
│       ├── hooks/                      ← Hooks
│       │   ├── useAuth.ts
│       │   ├── useDerivWS.ts
│       │   ├── useTicks.ts
│       │   └── useIndicators.ts
│       │
│       ├── components/                 ← Componentes
│       │   ├── layout/
│       │   │   ├── AppLayout.tsx       ← Layout principal (sidebar + topbar)
│       │   │   ├── Sidebar.tsx         ← Navegação lateral
│       │   │   └── TopBar.tsx          ← Status, saldo, profit, ping
│       │   │
│       │   ├── dashboard/
│       │   │   ├── StatusCard.tsx
│       │   │   ├── BalanceDisplay.tsx
│       │   │   ├── ProfitDisplay.tsx
│       │   │   └── PingDisplay.tsx
│       │   │
│       │   ├── trading/
│       │   │   ├── PageTabs.tsx
│       │   │   ├── PageControls.tsx
│       │   │   ├── TradeChart.tsx      ← Gráfico Lightweight Charts
│       │   │   ├── IndicatorOverlay.tsx
│       │   │   ├── OccurrenceList.tsx
│       │   │   └── ContractStatus.tsx
│       │   │
│       │   ├── strategy/
│       │   │   ├── CustomStrategyBuilder.tsx
│       │   │   ├── RuleRow.tsx
│       │   │   ├── ConditionEditor.tsx
│       │   │   ├── MarketSelector.tsx
│       │   │   └── DefenseConfig.tsx
│       │   │
│       │   ├── bankroll/
│       │   │   ├── MartingaleConfig.tsx
│       │   │   ├── StakeInput.tsx
│       │   │   ├── MiniMetaDialog.tsx
│       │   │   └── GlobalLimitsCard.tsx
│       │   │
│       │   ├── log/
│       │   │   └── LogViewer.tsx
│       │   │
│       │   └── common/
│       │       ├── Modal.tsx
│       │       ├── Button.tsx
│       │       ├── Input.tsx
│       │       ├── Select.tsx
│       │       └── Loading.tsx
│       │
│       └── pages/                      ← Páginas
│           ├── Login.tsx               ← Tela de login
│           ├── Dashboard.tsx           ← Cards de status
│           ├── OperationPage.tsx       ← Trading principal
│           ├── SetupManager.tsx        ← Gerenciar setups
│           ├── PatternAnalysis.tsx     ← Análise de padrões
│           ├── Calculator.tsx          ← Calculadora de multiplicador
│           └── Settings.tsx            ← Configurações
│
└── scripts/                            ← Scripts auxiliares
    ├── setup-dev.sh                    ← Setup automático do ambiente
    └── seed-data.py                    ← Dados iniciais do banco
```
