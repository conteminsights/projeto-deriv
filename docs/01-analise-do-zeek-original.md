# 01 — Análise Completa do ZeeK.Bot Original

> Documento gerado a partir de engenharia reversa do `ZeeK_Setup_3.1.0.exe`
> Data: 26/06/2026

---

## 1.1 Identificação

| Atributo | Valor |
|----------|-------|
| **Nome** | ZeeK.Bot |
| **Versão** | 3.1 (interna: V1.10 Rebuild) |
| **Instalador** | Inno Setup 6.7.0 |
| **Linguagem (app)** | Python 3.13 compilado com Nuitka + PyInstaller |
| **GUI** | PySide6 (Qt6) |
| **Autor** | Lukas Martins |
| **Contato** | zeekbot2020@gmail.com |
| **Site** | https://zeek.bot/ |
| **YouTube** | @zeekbot4020 |
| **Propósito** | Bot de trading para plataforma Deriv (opções binárias) |

---

## 1.2 Conexão com a Deriv

### WebSocket Principal
```
wss://ws.derivws.com/websockets/v3
App ID: 24332
```

### API REST
```
https://api.derivws.com
```

### Autenticação
- Token PAT (Personal Access Token) da Deriv
- O app envia `{"authorize": "<token>"}` após conectar
- Suporte a múltiplas contas por token (account switching)

### Fluxo de Conexão
1. Abrir WebSocket para `wss://ws.derivws.com/websockets/v3?app_id=24332`
2. Enviar `authorize` com o token PAT
3. Receber `authorize` response com `loginid`, `account_list`, `currency`, `balance`
4. Inscrever em ticks: `{"subscribe": 1, "ticks": "<symbol>"}`
5. Inscrever em balance: `{"subscribe": 1, "balance": 1}`
6. Inscrever em transaction: `{"subscribe": 1, "transaction": 1}`
7. Para cada operação: `proposal` → `buy` → monitorar `contract` status

### Símbolos (Mercados)
Os mercados disponíveis identificados no original:
```
R_100, R_75, R_50, R_25, R_10, 1HZ
```
E possivelmente outros sintéticos da Deriv.

---

## 1.3 Servidores Remotos

### Validação de Licença
```
POST http://79.143.190.252:8765/api/v1/license/validate
```

### Heartbeat / Monitor
```
POST http://79.143.190.252:8765/api/v1/monitor/heartbeat
```

### Configuração Remota
```
https://babutrader.com/path.json
```

O heartbeat envia periodicamente:
```json
{
  "instance_id": "zeek_<pid>",
  "status": "online",
  "token_hash": "<hash>",
  "account_name": "...",
  "loginid": "...",
  "balance": 123.45,
  "currency": "USD",
  "account_profit": 0.0,
  "uptime_seconds": 3600,
  "pages_count": 1,
  "pages": [...]
}
```

---

## 1.4 Estrutura de Dados (Configuração)

### Monitor Data (`zeek_monitor_data/zeek_<timestamp>_<pid>.json`)
```json
{
  "instance_id": "zeek_1782479517_43076",
  "pid": 43076,
  "status": "offline",
  "token_hash": "sem_token",
  "account_name": "—",
  "client_name": "—",
  "license_client_name": "",
  "loginid": "—",
  "license_key": "—",
  "balance": null,
  "currency": "",
  "account_profit": 0.0,
  "mini_meta_total": 0.0,
  "mini_meta_resets": 0,
  "mini_meta_enabled": false,
  "uptime_seconds": 0,
  "online": false,
  "pages_count": 1,
  "pages": [
    {
      "page": "Página 1",
      "market": "R_100",
      "mode": "CALL / PUT",
      "strategy": "CUSTOM",
      "operating": false,
      "defense": "SEM DEFESA",
      "session_profit": 0.0,
      "wins": 0,
      "losses": 0,
      "max_consecutive_loss": 0
    }
  ],
  "last_ping_ms": null,
  "ping_avg_ms": null,
  "updated_at": "2026-06-26 10:11:59",
  "version": "ZeeK 3.1",
  "vps_mode": false,
  "license_valid_until": "—",
  "license_status": "não validada",
  "license_allowed": false,
  "license_plan": ""
}
```

### Machine ID
Arquivo: `zeek_machine_id.txt`
Usado para vinculo de licença com hardware.

### Cache de Licença
Arquivo: `zeek_license_cache_<account_id>.json`
Evita revalidação a cada restart.

### Setups Salvos
Arquivo: `zeek_setups.json`
Contém as estratégias/páginas salvas pelo usuário no formato:
```json
{
  "setups": [
    {
      "name": "Setup 1",
      "pages": [...],
      "management": {...}
    }
  ]
}
```

---

## 1.5 Sistema de Licenciamento

- Licença baseada em email + machine_id + license_key
- Valida via HTTP no servidor remoto (79.143.190.252:8765)
- Cache local para evitar revalidação constante
- Status: "não validada", "válida", "bloqueada", "expirada"
- Planos de licença identificados: diferentes níveis de acesso
- Contato para renovação: zeekbot2020@gmail.com

---

## 1.6 Machine ID (`get_or_create_license_machine_id`)

```python
# Lógica inferida:
def get_or_create_license_machine_id():
    """
    - Verifica se zeek_machine_id.txt existe
    - Se não, gera um UUID único
    - Salva em:
        1. APPDATA/ZeeK/ (discreto)
        2. Pasta do executável (visível)
    - Marca a pasta como oculta no Windows (atributo +H)
    - Retorna o ID
    """
```

---

## 1.7 Estruturas Internas (Classes/Componentes)

### `ZeeKMultiWindow` — Janela principal
```
.__init__        -> Inicializa UI, workers, estado global
._build_ui       -> Monta layout completo
._left_panel     -> Painel esquerdo (controles globais)
._pages          -> Páginas de operação (abas)
._open_deriv_pat_pages -> Abre site para criar token
._login          -> Conecta com token PAT
._logout         -> Desconecta
._set_balance    -> Atualiza saldo
._set_connected  -> Atualiza estado de conexão
._on_tick        -> Processa tick recebido
._on_trade_event -> Processa resultado de trade
._fatal_error    -> Erro crítico
._sma_series     -> Calcula SMA
._ema_series     -> Calcula EMA
._bollinger_bands -> Calcula Bollinger
._rsi_series     -> Calcula RSI
._macd_values    -> Calcula MACD
```

### `OperationPage` — Página de operação
```
._build_ui       -> Layout da página
._place_order_ws -> Envia ordem pela WebSocket
._subscribe_tick_symbol -> Assina tick
._check_contract -> Verifica resultado
._apply_defense  -> Aplica sistema de defesa
```

### `CustomStrategyDialog` — Configurador de estratégia
```
.add_row         -> Adiciona regra
.load_rules      -> Carrega regras salvas
._custom_visual_rules -> Regras visuais customizadas
```

### `DerivMultiWorker` — Worker de conexão
```
._main                   -> Loop principal
._wait_authorize         -> Aguarda authorize
._subscribe_base         -> Assina canais base
._market_watchdog        -> Watchdog de mercado
.set_markets             -> Define mercados
._find_accounts          -> Descobre contas
._place_order_ws         -> Envia ordem
```

### `DerivWorker` — Worker por conta
```
._main           -> Loop principal por conta
._account_*      -> Gerenciamento de conta
```

### `PatternAnalysisDialog` — Análise de padrões
```
Análise de ticks históricos para detectar padrões
```

### `MultiplierCalculatorDialog` — Calculadora
```
Cálculo de multiplicador e stake
```

### `SetupManagerDialog` — Gerenciador de setups
```
Salvar, carregar, editar, excluir configurações
```

---

## 1.8 UI do ZeeK Original (referência visual)

A interface do ZeeK 3.1 tem:

**Painel Esquerdo:**
- Logo ASCII "ZEEK" + versão
- Seletor de modo (CALL/PUT | MULTIPLIER)
- Stake inicial, Multiplicador, Martingale
- Ajustável ao lucro
- Mini-meta (toggle + valor)
- Mxm entradas (toggle + valor)
- Modo VPS
- Auto-reload
- Limites globais de lucro/prejuízo

**Páginas (abas):**
- Múltiplas páginas renomeáveis
- Cada página: mercado, modo, estratégia
- Gráfico de ticks com indicadores
- Histórico de ocorrências
- Botões: Operar ON/OFF

**Topo:**
- Status da conexão
- Saldo + moeda
- Profit global
- Ping

**Log:**
- Dialog de log do sistema com compactação
- Filtro por símbolo

**Cores:**
- Tema escuro (dark)
- Tons de azul (#202832, #394554)
- Verde para profit (#00ff44)
- Vermelho para loss

---

## 1.9 Tecnologias Identificadas no Executável

| DLL/Pacote | Propósito |
|-----------|-----------|
| `PySide6/` (QtCore, QtGui, QtNetwork, QtWidgets) | GUI |
| `pythonnet/` | Integração .NET |
| `clr_loader/` | Carregador CLR (.NET) |
| `websockets/` (speedups.pyd) | WebSocket |
| `cryptography/` | Criptografia (licença) |
| `bcrypt/` | Hash (licença) |
| `markupsafe/` | Segurança HTML (logs?) |
| `win32api.pyd` | API Windows |
| `python313.dll` | Runtime Python 3.13 |
| `Nuitka` | Compilador Python→C++ |
| `Pyston` (bytecode archive) | Otimização Python |

---

## 1.10 Strings Relevantes Extras

```
"ZeeK.Bot Rebuild - V1.10 Layout + Gráfico dividido + Páginas"
"Base: Lukas Martins / ZeeK"
"Interface parecida com ZeeK antigo, login Deriv legacy e leitura ao vivo."
"Nesta V1.10 o sistema executa CUSTOM avançado com token antigo"
"Operação bloqueada: ZeeK sem WebSocket/licença operacional"
"OBRIGADO POR USAR O ZEEK 🤖💻"
"███████╗███████╗███████╗██╗  ██╗"  # ASCII art do logo
```

---

## 1.11 Comportamentos Identificados

1. **Reutilização de conta:** Se `auto_reuse_pat_account=True`, reusa conta após reset
2. **Reset controlado:** Fecha conexão por 60s e volta mantendo config
3. **Mini-meta:** Ao atingir meta, pausa e mostra "PARABÉNS"
4. **Mxm entradas:** Limite de entradas MASTER antes de reset
5. **Tick gap:** Detecta gaps de tick e loga
6. **Compactação de log:** Agrupa mensagens repetidas para não poluir
7. **Watchdog de mercado:** Reassina se detectar queda
8. **Modo VPS:** Para execução em servidor (sem UI ativa)
9. **Defesa BARREIRA:** Só opera após X losses consecutivos
10. **Soros SLAVE:** Copia operações do MASTER com barreira
