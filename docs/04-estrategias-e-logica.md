# 04 — Estratégias de Trading e Lógica do Motor

---

## 4.1 Visão Geral do Motor de Estratégias

O ZeeK original tem um motor de estratégias que opera em **páginas independentes**. Cada página tem:
- Um mercado (R_100, R_75...)
- Um modo (CALL/PUT ou MULTIPLIER)
- Uma estratégia (CUSTOM)
- Um sistema de defesa
- Estado de operação (ON/OFF)

As páginas operam **simultaneamente e independentemente**.

---

## 4.2 Estratégia CUSTOM

### Conceito
O CUSTOM é o coração do ZeeK. Ele permite definir **regras com gatilhos** baseados em:
- Preço atual vs indicadores técnicos
- Sequência de ticks
- Condições combinadas (AND/OR)

### Estrutura de uma Regra CUSTOM

```python
class CustomRule(BaseModel):
    """Uma regra individual na estratégia CUSTOM."""
    condition: TriggerCondition  # Condição do gatilho
    contract_type: Literal["CALL", "PUT"]
    duration: int = 1
    duration_unit: Literal["t", "s", "m", "h"] = "t"
    stake: float | None = None  # None = usar stake global

class TriggerCondition(BaseModel):
    """Condição para ativar o gatilho."""
    indicator: str  # "price", "sma", "ema", "rsi", "macd", "bb"
    operator: Literal[">", "<", ">=", "<=", "==", "cross_above", "cross_below"]
    value: float | str  # Valor fixo ou referência a outro indicador
    timeframe: int = 1  # Período do indicador (ex: SMA 20)

class CustomStrategy(BaseModel):
    """Estratégia CUSTOM completa."""
    rules: list[CustomRule]
    mode: Literal["AND", "OR"] = "AND"  # Todas devem ser true (AND) ou qualquer (OR)
    max_trades_per_tick: int = 1  # Máx contratos no mesmo tick
    cooldown_ticks: int = 0  # Ticks de espera entre contratos
```

### Exemplos de Regras

| Gatilho | Operador | Valor | Tradução |
|---------|----------|-------|----------|
| `price` | `>` | `sma_20` | Preço acima da SMA 20 → CALL |
| `rsi` | `<` | `30` | RSI abaixo de 30 → CALL (sobrevendido) |
| `rsi` | `>` | `70` | RSI acima de 70 → PUT (sobrecomprado) |
| `price` | `cross_above` | `bb_upper` | Preço cruzou Bollinger superior → PUT |
| `price` | `cross_below` | `bb_lower` | Preço cruzou Bollinger inferior → CALL |
| `macd` | `cross_above` | `macd_signal` | MACD cruzou acima da linha de sinal → CALL |
| `price` | `>` | `ema_50` | Preço acima da EMA 50 → CALL |

### Lógica de Avaliação (a cada tick)

```
PARA CADA página EM PÁGINAS ATIVAS:
    SE página.operando == OFF:
        CONTINUE
    
    PARA CADA regra EM página.regras:
        Calcular indicador (SMA, EMA, RSI, MACD, BB)
        Avaliar condição
        SE condição verdadeira:
            SE modo == "OR":
                ATIVAR gatilho → solicitar proposal
            SENÃO (AND):
                CONTINUE verificando próximas regras
    
    SE modo == "AND" E todas as regras verdadeiras:
        ATIVAR gatilho → solicitar proposal
    
    SE proposal aceito → comprar contrato
```

---

## 4.3 Sistema de Defesa

### Modos de Defesa

#### SEM DEFESA
Opera livremente sem restrições.

#### BARREIRA
```python
class BarrierDefense:
    """
    Só permite nova operação após X losses consecutivos.
    
    Funcionamento:
    - A cada WIN: reseta contador de losses consecutivos
    - A cada LOSS: incrementa contador
    - Se contador < barrier: NÃO opera (espera mais losses)
    - Se contador >= barrier: opera novamente
    - Ao WIN: reseta tudo
    
    Exemplo com barrier=3:
    LOSS, LOSS, LOSS → agora opera
    WIN → reseta
    LOSS, LOSS → ainda não opera (precisa de 3)
    """
    barrier: int = 3  # Nº de losses consecutivos necessários
    consecutive_losses: int = 0
    waiting_for_barrier: bool = False
```

#### SOROS MASTER / SLAVE

```python
class SorosDefense:
    """
    MASTER: Lidera as operações normalmente.
    SLAVE: Copia as operações do MASTER mas com barreira própria.
    
    Fluxo MASTER:
    1. Opera normalmente
    2. Quando tem LOSS: entra em modo "esperando"
    3. Continua operando até WIN
    4. Quando WIN: notifica SLAVEs
    
    Fluxo SLAVE:
    1. Não opera por conta própria (segue MASTER)
    2. Tem sua própria barreira (defense_barrier_mode)
    3. Se MASTER perdeu: SLAVE opera na direção oposta?
    4. Se MASTER ganhou: SLAVE copia?
    
    (Lógica exata precisa ser refinada com testes)
    """
    mode: Literal["MASTER", "SLAVE"]
    master_id: str | None = None  # Se SLAVE, qual MASTER segue
    barrier: int = 3
```

---

## 4.4 Gestão de Banca

### Stake Inicial
```python
initial_stake: float = 2.0  # USD
```

### Martingale
```python
class MartingaleConfig(BaseModel):
    """Progressão de stake após losses."""
    enabled: bool = False
    multiplier: float = 2.0  # Multiplica stake a cada loss
    max_steps: int = 5       # Máximo de progressões
    reset_on_win: bool = True
    
    # Exemplo: stake=2, multiplier=2
    # Win → stake volta pra 2
    # Loss → stake=4, Loss → stake=8, Loss → stake=16...
```

### Multiplicador
```python
class MultiplierConfig(BaseModel):
    """Stake baseada em múltiplo do lucro desejado."""
    enabled: bool = False
    target_multiplier: float = 1.0  # Ex: 1x o lucro desejado
```

### Ajustável ao Lucro
```python
class AdjustableStake(BaseModel):
    """Ajusta stake baseado no lucro atual."""
    enabled: bool = False
    # A cada X de lucro, aumenta stake em Y%
    # Ex: a cada $10 de lucro, stake sobe 0.50
    profit_step: float = 10.0
    stake_increment: float = 0.50
    max_stake: float = 50.0
```

---

## 4.5 Limites Globais

```python
class GlobalLimits(BaseModel):
    """Limites que afetam todas as páginas."""
    max_daily_profit: float | None = None  # Para tudo ao atingir
    max_daily_loss: float | None = None    # Para tudo ao atingir  
    max_consecutive_losses: int | None = 10 # Para tudo ao atingir
```

---

## 4.6 Mini-Meta

```python
class MiniMeta(BaseModel):
    """
    Meta de lucro parcial. Ao atingir:
    1. Fecha todas as páginas
    2. Mostra "PARABÉNS, META de $X atingida!"
    3. Reset controlado de 60s
    4. Volta operando normalmente
    
    Também faz reset controlado periódico:
    - A cada $X de lucro, reinicia conexão (evita detecção)
    """
    enabled: bool = False
    target_profit: float = 50.0
    reset_seconds: int = 60
```

---

## 4.7 Mxm Entradas (Máximo de Entradas)

```python
class MxmEntries(BaseModel):
    """
    Limita o número de entradas MASTER.
    Ao atingir o limite:
    1. Aguarda término dos contratos ativos
    2. Faz reset controlado
    3. Volta operando
    
    Útil para evitar sessions muito longas.
    """
    enabled: bool = False
    max_entries: int = 50
```

---

## 4.8 Auto-Reload

```python
class AutoReload(BaseModel):
    """
    Reinicia a conexão periodicamente para manter estabilidade.
    Só roda se TODAS as páginas estiverem seguras para reload
    (sem contratos ativos).
    
    Espera as páginas finalizarem antes de recarregar.
    """
    enabled: bool = False
    interval_minutes: int = 60
```

---

## 4.9 Indicadores Técnicos Implementados

### SMA (Simple Moving Average)
```python
def sma(values: list[float], period: int) -> list[float]:
    """Média aritmética dos últimos N ticks."""
    result = []
    for i in range(len(values)):
        if i < period - 1:
            result.append(None)
        else:
            result.append(sum(values[i-period+1:i+1]) / period)
    return result
```

### EMA (Exponential Moving Average)
```python
def ema(values: list[float], period: int) -> list[float]:
    """Média móvel exponencial (mais peso nos ticks recentes)."""
    k = 2 / (period + 1)
    result = []
    ema_prev = None
    for i, price in enumerate(values):
        if ema_prev is None:
            ema_prev = price
            result.append(None if i < period - 1 else price)
        else:
            ema_val = price * k + ema_prev * (1 - k)
            ema_prev = ema_val
            result.append(ema_val if i >= period - 1 else None)
    return result
```

### RSI (Relative Strength Index)
```python
def rsi(values: list[float], period: int = 14) -> list[float]:
    """Mede velocidade e magnitude das mudanças de preço."""
    if len(values) < period + 1:
        return [None] * len(values)
    
    gains, losses = [], []
    for i in range(1, len(values)):
        diff = values[i] - values[i-1]
        gains.append(max(diff, 0))
        losses.append(max(-diff, 0))
    
    result = [None] * period
    avg_gain = sum(gains[:period]) / period
    avg_loss = sum(losses[:period]) / period
    
    for i in range(period, len(gains)):
        if avg_loss == 0:
            rs = float('inf')
        else:
            rs = avg_gain / avg_loss
        result.append(100 - (100 / (1 + rs)))
        
        avg_gain = (avg_gain * (period - 1) + gains[i]) / period
        avg_loss = (avg_loss * (period - 1) + losses[i]) / period
    
    return result
```

### Bollinger Bands
```python
def bollinger_bands(values: list[float], period: int = 20, deviation: float = 2.0):
    """Bandas de volatilidade ao redor da SMA."""
    middle = sma(values, period)
    result_middle, result_upper, result_lower = [], [], []
    
    for i in range(len(values)):
        if middle[i] is None:
            result_middle.append(None)
            result_upper.append(None)
            result_lower.append(None)
        else:
            window = values[max(0, i-period+1):i+1]
            std = statistics.stdev(window) if len(window) > 1 else 0
            result_middle.append(middle[i])
            result_upper.append(middle[i] + deviation * std)
            result_lower.append(middle[i] - deviation * std)
    
    return result_middle, result_upper, result_lower
```

### MACD
```python
def macd(values: list[float], fast: int = 12, slow: int = 26, signal: int = 9):
    """Moving Average Convergence Divergence."""
    ema_fast = ema(values, fast)
    ema_slow = ema(values, slow)
    
    macd_line = []
    for i in range(len(values)):
        if ema_fast[i] is None or ema_slow[i] is None:
            macd_line.append(None)
        else:
            macd_line.append(ema_fast[i] - ema_slow[i])
    
    signal_line = ema([v for v in macd_line if v is not None], signal)
    # Reconstruir com None nos lugares certos
    
    histogram = []
    # histogram = macd_line - signal_line
    
    return macd_line, signal_line, histogram
```

---

## 4.10 Análise de Padrões

O ZeeK tem uma ferramenta de análise de padrões que:
1. Carrega ticks históricos de um período
2. Identifica ocorrências onde a estratégia teria entrado
3. Calcula win rate, profit, drawdown
4. Mostra resultados visuais

```python
class PatternAnalysis:
    """Analisa ticks históricos para validar estratégias."""
    
    async def analyze(
        self,
        symbol: str,
        start_date: datetime,
        end_date: datetime,
        strategy: CustomStrategy
    ) -> PatternAnalysisResult:
        """Executa backtest da estratégia nos ticks."""
        ticks = await self._load_ticks(symbol, start_date, end_date)
        occurrences = []
        
        for tick in ticks:
            signal = self._evaluate_rules(strategy, tick, ticks)
            if signal:
                occurrences.append(Occurrence(
                    tick_epoch=tick.epoch,
                    tick_price=tick.price,
                    signal=signal,
                    result=None  # Simular resultado?
                ))
        
        return PatternAnalysisResult(
            total_ticks=len(ticks),
            occurrences=occurrences,
            win_count=..., loss_count=...,
            total_profit=..., max_drawdown=...
        )
```

---

## 4.11 Estrutura de uma Página de Operação

```python
class OperationPage(BaseModel):
    """Uma página/tab de operação no ZeeK."""
    id: str
    name: str  # "Página 1", "Página 2"...
    market: str  # "R_100"
    mode: Literal["CALL_PUT", "MULTIPLIER"]
    strategy: StrategyConfig
    defense: DefenseConfig
    operating: bool = False
    
    # Estado vivo (não persistido)
    consecutive_losses: int = 0
    session_profit: float = 0.0
    wins: int = 0
    losses: int = 0
    max_consecutive_loss: int = 0
    active_contract_id: str | None = None
```

---

## 4.12 Gerenciamento de Configuração (Setups)

```python
class Setup(BaseModel):
    """Um setup salvo (estratégia completa)."""
    id: str
    name: str
    pages: list[OperationPage]
    management: ManagementConfig  # Configurações globais
    created_at: datetime
    updated_at: datetime

class ManagementConfig(BaseModel):
    """Configurações de gerenciamento."""
    initial_stake: float = 2.0
    martingale: MartingaleConfig = MartingaleConfig()
    adjustable: AdjustableStake = AdjustableStake()
    mini_meta: MiniMeta = MiniMeta()
    mxm_entries: MxmEntries = MxmEntries()
    auto_reload: AutoReload = AutoReload()
    global_limits: GlobalLimits = GlobalLimits()
```
