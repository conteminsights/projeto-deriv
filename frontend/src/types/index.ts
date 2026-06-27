// Tipos compartilhados para o frontend do Contêm Insights Trade

// ─── Auth ──────────────────────────
export interface LoginResponse {
  access_token: string
  token_type: string
  user_id: number
  email: string
}

export interface User {
  id: number
  email: string
}

// ─── Deriv ─────────────────────────
export interface Tick {
  epoch: number
  quote: number
  symbol: string
}

export interface Balance {
  balance: number
  currency: string
}

export interface DerivStatus {
  connected: boolean
  balance: Balance | null
  active_symbols: string[]
}

// ─── Strategy / Setup ──────────────
export interface TriggerCondition {
  indicator: string
  operator: string
  value: number
  timeframe: number
}

export interface Rule {
  condition: TriggerCondition
  contract_type: 'CALL' | 'PUT'
  duration: number
  duration_unit: string
}

export interface PageConfig {
  name: string
  market: string
  mode: string
  rules: Rule[]
}

export interface ManagementConfig {
  initial_stake: number
  martingale_enabled: boolean
  martingale_multiplier: number
  martingale_max_steps: number
  multiplier_enabled: boolean
  multiplier_value: number
  defense_mode: string
  profit_target: number | null
  loss_limit: number | null
}

export interface Strategy {
  id: number
  user_id: number
  name: string
  description: string
  is_builtin: boolean
  pages: PageConfig[]
  management: ManagementConfig
  created_at: string
  updated_at: string | null
}

// ─── WS Messages ───────────────────
export type WSMessage =
  | { type: 'tick'; symbol: string; tick: Tick }
  | { type: 'balance'; balance: Balance }
  | { type: 'deriv_status'; connected: boolean }
  | { type: 'status'; connected: boolean; balance: Balance | null; active_symbols: string[] }
  | { type: 'subscribed'; symbol: string; success: boolean }
  | { type: 'unsubscribed'; symbol: string }
  | { type: 'error'; message: string }
  | { type: 'contracts'; contracts: any[] }
  | { type: 'deriv_connecting'; message: string }
  | { type: 'deriv_disconnected' }

// ─── Bankroll ──────────────────────
export interface BankrollConfig {
  initial_stake: number
  current_stake: number
  martingale: { enabled: boolean; multiplier: number; max_steps: number }
  multiplier: { enabled: boolean; value: number }
  mini_meta: { enabled: boolean; profit_target: number; max_entries: number }
  limits: {
    enabled: boolean
    daily_loss_limit: number
    daily_profit_target: number
    session_loss_limit: number
    consecutive_loss_limit: number
  }
  auto_reload: { enabled: boolean; reload_after_minutes: number; reload_after_entries: number }
}

export interface BankrollState {
  current_stake: number
  session_profit: number
  daily_profit: number
  consecutive_losses: number
  martingale_step: number
  session_entries: number
  stopped: boolean
}

export interface BankrollResponse {
  config: BankrollConfig
  state: BankrollState
}

// ─── Trade ─────────────────────────
export interface Trade {
  contract_id: string
  symbol: string
  contract_type: string
  stake: number
  buy_price: number
  profit?: number
  status: string
  entry_tick?: number
  exit_tick?: number
}

// ─── Defense ───────────────────────
export interface DefenseState {
  page_id: string
  mode: string
  barrier: number
  consecutive_losses: number
  waiting_for_barrier: boolean
}
