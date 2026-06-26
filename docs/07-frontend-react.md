# 07 — Frontend React — Especificação

> Framework: React 18+ com Vite, TypeScript, TailwindCSS, Zustand, Lightweight Charts

---

## 7.1 Estrutura de Arquivos

```
frontend/
├── src/
│   ├── main.tsx
│   ├── App.tsx
│   ├── index.css
│   ├── vite-env.d.ts
│   │
│   ├── types/              # Tipos TypeScript
│   │   ├── deriv.ts        # Tipos da API Deriv
│   │   ├── strategy.ts     # Estratégias e regras
│   │   ├── trade.ts        # Contratos e trades
│   │   └── user.ts         # Usuário e auth
│   │
│   ├── services/           # Serviços
│   │   ├── api.ts          # REST client (axios)
│   │   ├── ws.ts           # WebSocket client
│   │   └── deriv.ts        # Helpers Deriv
│   │
│   ├── store/              # Estado global (Zustand)
│   │   ├── authStore.ts
│   │   ├── derivStore.ts
│   │   ├── strategyStore.ts
│   │   └── uiStore.ts
│   │
│   ├── hooks/              # Hooks
│   │   ├── useAuth.ts
│   │   ├── useDerivWS.ts
│   │   ├── useTicks.ts
│   │   └── useIndicators.ts
│   │
│   ├── components/         # Componentes
│   │   ├── layout/
│   │   │   ├── AppLayout.tsx
│   │   │   ├── Sidebar.tsx
│   │   │   └── TopBar.tsx
│   │   │
│   │   ├── dashboard/
│   │   │   ├── StatusCard.tsx
│   │   │   ├── BalanceDisplay.tsx
│   │   │   ├── ProfitDisplay.tsx
│   │   │   └── PingDisplay.tsx
│   │   │
│   │   ├── trading/
│   │   │   ├── PageTabs.tsx
│   │   │   ├── PageControls.tsx
│   │   │   ├── TradeChart.tsx
│   │   │   ├── IndicatorOverlay.tsx
│   │   │   ├── OccurrenceList.tsx
│   │   │   └── ContractStatus.tsx
│   │   │
│   │   ├── strategy/
│   │   │   ├── CustomStrategyBuilder.tsx
│   │   │   ├── RuleRow.tsx
│   │   │   ├── ConditionEditor.tsx
│   │   │   ├── MarketSelector.tsx
│   │   │   └── DefenseConfig.tsx
│   │   │
│   │   ├── bankroll/
│   │   │   ├── MartingaleConfig.tsx
│   │   │   ├── StakeInput.tsx
│   │   │   ├── MiniMetaDialog.tsx
│   │   │   └── GlobalLimitsCard.tsx
│   │   │
│   │   ├── log/
│   │   │   └── LogViewer.tsx
│   │   │
│   │   └── common/
│   │       ├── Modal.tsx
│   │       ├── Button.tsx
│   │       ├── Input.tsx
│   │       ├── Select.tsx
│   │       └── Loading.tsx
│   │
│   ├── pages/
│   │   ├── Login.tsx
│   │   ├── Dashboard.tsx
│   │   ├── OperationPage.tsx      # Página de trading principal
│   │   ├── SetupManager.tsx
│   │   ├── PatternAnalysis.tsx
│   │   ├── Calculator.tsx
│   │   └── Settings.tsx
│   │
│   └── theme.ts
│
├── public/
├── package.json
├── tsconfig.json
├── vite.config.ts
├── tailwind.config.js
├── postcss.config.js
└── Dockerfile
```

---

## 7.2 Estado Global (Zustand)

### authStore
```typescript
interface AuthState {
  user: User | null;
  token: string | null;       // JWT
  derivToken: string | null;  // PAT token (criptografado)
  isAuthenticated: boolean;
  
  login: (email: string, password: string) => Promise<void>;
  logout: () => void;
  setDerivToken: (token: string) => void;
}
```

### derivStore
```typescript
interface DerivState {
  // Conexão
  connected: boolean;
  authorizing: boolean;
  authorized: boolean;
  error: string | null;
  
  // Conta
  loginid: string | null;
  balance: number | null;
  currency: string | null;
  accountList: Account[];
  
  // Mercados
  subscribedMarkets: string[];
  ticks: Record<string, Tick[]>;  // symbol → ticks
  
  // Ações
  connect: (token: string) => Promise<void>;
  disconnect: () => void;
  subscribeMarket: (symbol: string) => void;
  unsubscribeMarket: (symbol: string) => void;
}
```

### strategyStore
```typescript
interface StrategyState {
  // Páginas
  pages: OperationPage[];
  activePageIndex: number;
  
  // Configurações globais
  initialStake: number;
  martingale: MartingaleConfig;
  adjustable: AdjustableConfig;
  miniMeta: MiniMetaConfig;
  mxmEntries: MxmEntriesConfig;
  autoReload: AutoReloadConfig;
  globalLimits: GlobalLimits;
  
  // Ações
  addPage: (page: Partial<OperationPage>) => void;
  removePage: (index: number) => void;
  updatePage: (index: number, updates: Partial<OperationPage>) => void;
  toggleOperation: (index: number) => void;
  loadSetup: (setup: Setup) => void;
  saveCurrentSetup: () => Promise<void>;
  loadSetups: () => Promise<void>;
}
```

---

## 7.3 Roteamento

```typescript
<Routes>
  <Route path="/login" element={<Login />} />
  <Route path="/" element={<AppLayout />}>
    <Route index element={<Navigate to="/dashboard" />} />
    <Route path="dashboard" element={<Dashboard />} />
    <Route path="trade" element={<OperationPage />} />
    <Route path="setups" element={<SetupManager />} />
    <Route path="patterns" element={<PatternAnalysis />} />
    <Route path="calculator" element={<Calculator />} />
    <Route path="settings" element={<Settings />} />
  </Route>
</Routes>
```

---

## 7.4 Tema Visual (Baseado no ZeeK Original)

### Cores
```typescript
const theme = {
  colors: {
    // Fundo
    bgPrimary: '#09091f',     // Fundo principal (dark navy)
    bgSecondary: '#11182d',   // Cards
    bgTertiary: '#1a2340',    // Inputs, tabelas
    
    // Bordas
    border: '#202832',        // Bordas padrão
    borderLight: '#394554',   // Hover / active
    
    // Texto
    textPrimary: '#e0e6f0',
    textSecondary: '#8892a8',
    textMuted: '#5a6478',
    
    // Acento
    accent: '#3b82f6',         // Azul (links, botões)
    accentLight: '#60a5fa',    // Hover
    accentDark: '#1d4ed8',     // Active
    
    // Trading
    profit: '#00ff44',        // Verde profit
    loss: '#ff4444',          // Vermelho loss
    warning: '#ffaa00',
    
    // Modo CALL/PUT
    callColor: '#00c853',     // Verde CALL
    putColor: '#ff1744',      // Vermelho PUT
  },
  borderRadius: {
    sm: '4px',
    md: '8px',
    lg: '12px',
  },
  fontFamily: "'Inter', 'Segoe UI', sans-serif",
}
```

### Componentes de Referência (do ZeeK Original)
- **Logo ASCII:** `███████╗███████╗███████╗██╗  ██╗`
- **Layout:** Painel esquerdo (controles) + área principal (páginas com abas)
- **Fonte:** Monospace para logs, sans-serif para UI

---

## 7.5 WebSocket Bidirecional

### Conexão Frontend ↔ Backend

```typescript
// frontend/src/services/ws.ts
class TradingWS {
  private ws: WebSocket | null = null;
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null;
  
  connect(token: string) {
    this.ws = new WebSocket(`ws://localhost:8000/ws?token=${token}`);
    
    this.ws.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      switch (msg.type) {
        case 'tick':
          derivStore.getState().addTick(msg.symbol, msg.tick);
          break;
        case 'balance':
          derivStore.getState().setBalance(msg.balance);
          break;
        case 'contract_result':
          strategyStore.getState().handleContractResult(msg);
          break;
        case 'connection_status':
          derivStore.getState().setConnectionStatus(msg.status);
          break;
      }
    };
  }
  
  send(action: string, payload: any) {
    this.ws?.send(JSON.stringify({ action, ...payload }));
  }
  
  // Ações que o frontend pode enviar:
  // - { action: 'start_page', page_id: '...' }
  // - { action: 'stop_page', page_id: '...' }
  // - { action: 'update_strategy', page_id: '...', strategy: {...} }
  // - { action: 'request_ticks', symbol: 'R_100', count: 100 }
}
```

---

## 7.6 Gráfico de Ticks (Lightweight Charts)

### Configuração
```typescript
// frontend/src/components/TradeChart.tsx
import { createChart, IChartApi } from 'lightweight-charts';

class TradeChart {
  private chart: IChartApi;
  private candlestickSeries: ISeriesApi<'Candlestick'>;
  
  constructor(container: HTMLElement) {
    this.chart = createChart(container, {
      layout: {
        background: { color: '#11182d' },
        textColor: '#8892a8',
      },
      grid: {
        vertLines: { color: '#1a2340' },
        horzLines: { color: '#1a2340' },
      },
      timeScale: {
        timeVisible: true,
        secondsVisible: false,
      },
      crosshair: {
        mode: CrosshairMode.Normal,
      },
    });
  }
  
  // Adicionar linhas de indicadores
  addSMALine(values: (number | null)[]) { ... }
  addBBLines(middle: number[], upper: number[], lower: number[]) { ... }
  addRSI(panel: ISeriesApi<'Line'>, values: (number | null)[]) { ... }
  
  // Marcar ocorrências (entradas)
  addEntryMarker(time: number, type: 'CALL' | 'PUT') { ... }
  addResultMarker(time: number, result: 'win' | 'loss') { ... }
}
```

### Layout do Gráfico
```
┌──────────────────────────────────────┐
│  Painel Principal: Preço + SMA + BB  │  70% altura
│                                      │
│  ┌─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┬─┐   │
│  │ │ │ │ │ │ │ │ │ │ │ │ │ │ │ │   │
│  └─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┴─┘   │
├──────────────────────────────────────┤
│  Painel RSI                          │  15% altura
├──────────────────────────────────────┤
│  Painel MACD                         │  15% altura
└──────────────────────────────────────┘
```

---

## 7.7 Configurador CUSTOM (UI)

### Layout do Configurador
```
┌─────────────────────────────────────────────┐
│  CONFIGURAÇÃO CUSTOM                         │
├─────────────────────────────────────────────┤
│  [Mercado: R_100 ▾]  [Modo: AND ▾]          │
├─────────────────────────────────────────────┤
│  REGRAS:                                     │
│  ┌─────────────────────────────────────────┐ │
│  │ SE [SMA 20 ▾] [> ▾] [EMA 50 ▾] → CALL  │ │
│  │ Duração: [1 ▾] [t ▾]  [X]               │ │
│  ├─────────────────────────────────────────┤ │
│  │ SE [RSI ▾] [< ▾] [30]      → CALL      │ │
│  │ Duração: [1 ▾] [t ▾]  [X]               │ │
│  ├─────────────────────────────────────────┤ │
│  │ SE [Price ▾] [cross_above ▾] [BB_UPPER] │ │
│  │ → PUT  Duração: [2 ▾] [t ▾]  [X]        │ │
│  └─────────────────────────────────────────┘ │
│  [+ ADD REGRA]                               │
├─────────────────────────────────────────────┤
│  [SALVAR] [SALVAR COMO SETUP] [FECHAR]      │
└─────────────────────────────────────────────┘
```

---

## 7.8 Responsividade

O layout é pensado para **desktop** (operação de trading), mas funcional em tablets:

### Breakpoints
```css
/* Tailwind config */
screens: {
  'sm': '640px',   /* Tablet retrato */
  'md': '768px',   /* Tablet paisagem */
  'lg': '1024px',  /* Desktop */
  'xl': '1280px',  /* Desktop wide */
  '2xl': '1536px', /* Ultrawide */
}
```

### Comportamento Mobile
- Sidebar vira drawer (hamburger)
- Gráfico ocupa tela cheia
- Controles em bottom sheet
- Abas em scroll horizontal
