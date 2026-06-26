# 08 — Backend FastAPI — Especificação

---

## 8.1 Estrutura de Diretórios

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py                    # Entrypoint FastAPI
│   │
│   ├── config.py                  # Configurações (pydantic-settings)
│   │
│   ├── api/
│   │   ├── __init__.py
│   │   ├── router.py              # Router principal (agrega todos)
│   │   ├── auth.py                # POST /auth/login, /auth/register
│   │   ├── tokens.py              # CRUD tokens PAT
│   │   ├── status.py              # GET /status (conexão, saldo)
│   │   ├── strategies.py          # CRUD estratégias
│   │   ├── bankroll.py            # Config de banca
│   │   ├── trades.py              # Histórico de trades
│   │   ├── setups.py              # CRUD setups
│   │   └── ws.py                  # WebSocket /ws (tempo real)
│   │
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py            # JWT, hash, criptografia
│   │   ├── database.py            # SQLAlchemy engine + session
│   │   └── exceptions.py          # Error handlers
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── user.py                # User SQLAlchemy model
│   │   ├── token.py               # DerivToken SQLAlchemy model
│   │   ├── trade.py               # Trade SQLAlchemy model
│   │   ├── strategy.py            # Pydantic models (estratégias)
│   │   └── setup.py               # Setup SQLAlchemy model
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── deriv_client.py        # Cliente WebSocket Deriv
│   │   ├── market_manager.py      # Gerencia mercados/assinaturas
│   │   ├── strategy_engine.py     # Motor de estratégia CUSTOM
│   │   ├── rule_engine.py         # Avaliador de regras/gatilhos
│   │   ├── order_manager.py       # Envio de ordens
│   │   ├── indicators.py          # Indicadores técnicos
│   │   ├── bankroll.py            # Gestão de banca
│   │   ├── defense.py             # Sistema de defesa
│   │   ├── soros.py               # Soros MASTER/SLAVE
│   │   ├── page_manager.py        # Gerenciamento multi-página
│   │   ├── pattern_analyzer.py    # Análise de padrões
│   │   └── license.py             # Validação de licença
│   │
│   ├── workers/
│   │   ├── __init__.py
│   │   ├── deriv_worker.py        # Worker de conexão Deriv
│   │   └── monitor.py             # Heartbeat monitor
│   │
│   └── schemas/
│       ├── __init__.py
│       ├── auth.py                # Pydantic schemas de auth
│       ├── trade.py               # Pydantic schemas de trade
│       └── strategy.py            # Pydantic schemas de estratégia
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py                # Fixtures
│   ├── test_auth.py
│   ├── test_deriv_client.py
│   ├── test_strategy.py
│   ├── test_indicators.py
│   └── test_bankroll.py
│
├── alembic/
│   └── versions/
│
├── requirements.txt
├── Dockerfile
└── .env.example
```

---

## 8.2 API REST — Endpoints

### Autenticação

```http
POST /api/auth/register
Body: { "email": "...", "password": "..." }
Response: { "id": 1, "email": "...", "created_at": "..." }

POST /api/auth/login
Body: { "email": "...", "password": "..." }
Response: { "access_token": "jwt...", "token_type": "bearer" }

POST /api/auth/refresh
Header: Authorization: Bearer <token>
Response: { "access_token": "jwt..." }
```

### Tokens PAT (Deriv)

```http
GET    /api/tokens          → Lista tokens (parcialmente ocultos)
POST   /api/tokens          → Salva novo token PAT
DELETE /api/tokens/:id      → Remove token

POST   /api/tokens/:id/connect  → Conecta na Deriv com este token
POST   /api/tokens/disconnect   → Desconecta
```

### Status

```http
GET /api/status
→ { "connected": true, "loginid": "CR1234567", "balance": 1000.00,
    "currency": "USD", "markets": ["R_100"], "uptime": 3600, "ping": 45 }

GET /api/status/accounts
→ { "accounts": [{ "loginid": "...", "currency": "USD", "is_virtual": false }] }
```

### Páginas / Operação

```http
GET    /api/pages           → Lista páginas atuais
POST   /api/pages           → Cria nova página
PUT    /api/pages/:id       → Atualiza página
DELETE /api/pages/:id       → Remove página
POST   /api/pages/:id/start → Inicia operação na página
POST   /api/pages/:id/stop  → Para operação na página
```

### Estratégias CUSTOM

```http
GET    /api/strategies                     → Lista estratégias salvas
POST   /api/strategies                     → Salva nova estratégia
GET    /api/strategies/:id                 → Detalhes
PUT    /api/strategies/:id                 → Atualiza
DELETE /api/strategies/:id                 → Remove
POST   /api/strategies/evaluate            → Avalia regras contra ticks atuais
```

### Bancas / Configuração

```http
GET  /api/bankroll       → Config atual
PUT  /api/bankroll       → Atualiza config
GET  /api/bankroll/stats → Estatísticas (profit, wins, losses)
```

### Trades (Histórico)

```http
GET /api/trades              → Lista trades (paginado)
GET /api/trades/:id          → Detalhes do trade
GET /api/trades/stats        → Estatísticas agregadas
     ?period=7d              → Filtro por período
```

### Setups

```http
GET    /api/setups          → Lista setups salvos
POST   /api/setups          → Salva setup atual
GET    /api/setups/:id      → Carrega setup
PUT    /api/setups/:id      → Atualiza setup
DELETE /api/setups/:id      → Remove setup
POST   /api/setups/:id/load → Aplica setup (ativa páginas)
```

### Análise de Padrões

```http
POST /api/patterns/analyze
Body: { "symbol": "R_100", "start": "2026-01-01", "end": "2026-06-26",
        "strategy_id": 1 }
Response: { "total_ticks": 100000, "occurrences": [...], "win_rate": 0.65,
            "total_profit": 123.45 }

GET /api/patterns/history?symbol=R_100&start=...&end=...
→ Lista ticks históricos para análise manual
```

---

## 8.3 WebSocket — `/ws`

### Conexão
```
ws://localhost:8000/ws?token=<jwt>
```

### Mensagens do Servidor → Cliente
```json
{"type": "connection_status", "status": "connected"}
{"type": "tick", "symbol": "R_100", "epoch": 1234567890, "price": 1234.56}
{"type": "balance", "balance": 1000.00, "currency": "USD"}
{"type": "contract_result", "page_id": "1", "contract_id": 123456789, "profit": 9.85, "status": "won"}
{"type": "trade_update", "page_id": "1", "wins": 5, "losses": 2, "session_profit": 23.40}
{"type": "defense_status", "page_id": "1", "defense": "waiting_barrier", "consecutive_losses": 2}
{"type": "mini_meta", "status": "reached", "profit": 50.00}
{"type": "error", "code": "...", "message": "..."}
```

### Mensagens do Cliente → Servidor
```json
{"action": "start_page", "page_id": "1"}
{"action": "stop_page", "page_id": "1"}
{"action": "update_page", "page_id": "1", "market": "R_100", "strategy": {...}}
{"action": "subscribe_ticks", "symbol": "R_100"}
{"action": "request_history", "symbol": "R_100", "count": 500}
```

---

## 8.4 Workers

### Deriv Worker
```python
class DerivWorker(ABC):
    """Worker base para conexão com a Deriv."""
    
    async def run(self):
        """Loop principal do worker."""
        while not self._stop_event.is_set():
            try:
                await self.connect()
                await self.authorize()
                await self.subscribe_channels()
                await self.message_loop()
            except Exception as e:
                logger.error(f"Worker error: {e}")
                await asyncio.sleep(self._backoff())
    
    @abstractmethod
    async def on_tick(self, tick: Tick):
        """Processa tick recebido."""
        pass
    
    @abstractmethod
    async def on_balance(self, balance: BalanceUpdate):
        """Atualização de saldo."""
        pass
    
    @abstractmethod
    async def on_transaction(self, transaction: Transaction):
        """Notificação de transação."""
        pass
```

### Monitor Worker
```python
class MonitorWorker:
    """Envia heartbeats para o servidor de monitoramento."""
    
    async def run(self):
        while True:
            await asyncio.sleep(60)  # A cada 60s
            payload = self._build_payload()
            try:
                await self._send_heartbeat(payload)
            except Exception as e:
                logger.warning(f"Heartbeat failed: {e}")
```

---

## 8.5 Dependências (requirements.txt)

```
# Framework
fastapi==0.115.*
uvicorn[standard]==0.34.*
pydantic==2.10.*
pydantic-settings==2.7.*

# Database
sqlalchemy==2.0.*
alembic==1.14.*
aiosqlite==0.20.*  # SQLite async

# WebSocket
websockets==14.*

# Auth
python-jose[cryptography]==3.3.*
passlib[bcrypt]==1.7.*
python-multipart==0.0.*

# Cache / Queue
redis==5.2.*
celery==5.4.*  # opcional

# HTTP Client
httpx==0.28.*

# Utilitários
python-dotenv==1.0.*
arrow==1.3.*  # Datas

# Test
pytest==8.3.*
pytest-asyncio==0.24.*
httpx==0.28.*
```

---

## 8.6 Configuração (.env.example)

```env
# App
APP_NAME=ZeeK.Web
DEBUG=true
SECRET_KEY=change-me-in-production
ACCESS_TOKEN_EXPIRE_MINUTES=1440

# Database
DATABASE_URL=sqlite+aiosqlite:///./zeek.db
# DATABASE_URL=postgresql+asyncpg://user:pass@localhost/zeek

# Redis (opcional, para filas)
REDIS_URL=redis://localhost:6379

# Deriv
DERIV_APP_ID=24332
DERIV_WS_URL=wss://ws.derivws.com/websockets/v3
DERIV_API_URL=https://api.derivws.com

# Monitor (servidor de licença)
MONITOR_URL=http://79.143.190.252:8765/api/v1
MONITOR_ENABLED=false

# CORS
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# License
LICENSE_VALIDATION_URL=http://79.143.190.252:8765/api/v1/license/validate
```

---

## 8.7 Modelos de Dados (SQLAlchemy)

### User
```python
class User(Base):
    __tablename__ = "users"
    
    id: int = Column(Integer, primary_key=True)
    email: str = Column(String(255), unique=True, nullable=False)
    hashed_password: str = Column(String(255), nullable=False)
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, onupdate=func.now())
    
    # Relacionamentos
    tokens: list[DerivToken] = relationship("DerivToken", back_populates="user")
    setups: list[Setup] = relationship("Setup", back_populates="user")
    trades: list[Trade] = relationship("Trade", back_populates="user")
```

### DerivToken
```python
class DerivToken(Base):
    __tablename__ = "deriv_tokens"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    token_hash: str = Column(String(255), nullable=False)  # Hash do token
    token_encrypted: str = Column(Text, nullable=False)    # Token criptografado
    label: str = Column(String(100), default="")
    is_active: bool = Column(Boolean, default=True)
    last_used: datetime | None = Column(DateTime, nullable=True)
    created_at: datetime = Column(DateTime, default=func.now())
```

### Trade
```python
class Trade(Base):
    __tablename__ = "trades"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    page_id: str = Column(String(50))
    setup_name: str = Column(String(100))
    
    # Contrato
    contract_id: str = Column(String(100), unique=True)
    symbol: str = Column(String(20))
    contract_type: str = Column(String(20))  # CALL, PUT, MULTIPLIER
    stake: float = Column(Float)
    payout: float | None = Column(Float, nullable=True)
    profit: float | None = Column(Float, nullable=True)
    
    # Resultado
    status: str = Column(String(20))  # pending, won, lost, sold
    entry_tick: float = Column(Float)
    exit_tick: float | None = Column(Float, nullable=True)
    entry_epoch: int = Column(Integer)
    exit_epoch: int | None = Column(Integer, nullable=True)
    
    # Estratégia aplicada
    strategy_snapshot: str = Column(Text)  # JSON da estratégia
    
    created_at: datetime = Column(DateTime, default=func.now())
```

### Setup
```python
class Setup(Base):
    __tablename__ = "setups"
    
    id: int = Column(Integer, primary_key=True)
    user_id: int = Column(Integer, ForeignKey("users.id"))
    name: str = Column(String(100))
    description: str = Column(String(500), default="")
    is_builtin: bool = Column(Boolean, default=False)  # Setups padrão do ZeeK
    
    # Serialização das páginas + config
    pages_data: str = Column(Text)  # JSON com lista de páginas
    management_data: str = Column(Text)  # JSON com config de banca
    
    created_at: datetime = Column(DateTime, default=func.now())
    updated_at: datetime = Column(DateTime, onupdate=func.now())
```
