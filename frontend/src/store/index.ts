// Global state store
import { create } from 'zustand'
import type { Tick, Balance, Strategy, BankrollResponse, DerivStatus } from '../types'

interface AppState {
  // Auth
  token: string | null
  userId: number | null
  email: string | null

  // Deriv
  derivConnected: boolean
  balance: Balance | null
  activeSymbols: string[]
  ticks: Record<string, Tick[]>

  // Bankroll
  bankroll: BankrollResponse | null

  // Strategies
  strategies: Strategy[]

  // Operating
  operating: boolean
  operatingPage: string | null

  // UI
  isConnecting: boolean
  error: string | null
  accounts: any[]
  currentLoginid: string | null

  // Actions
  setAuth: (token: string, userId: number, email: string) => void
  logout: () => void
  setDerivStatus: (status: DerivStatus) => void
  addTick: (symbol: string, tick: Tick) => void
  setBankroll: (data: BankrollResponse) => void
  setStrategies: (list: Strategy[]) => void
  setOperating: (active: boolean, pageId?: string) => void
  setAccounts: (accounts: any[], loginid: string | null) => void
  setConnecting: (v: boolean) => void
  setError: (msg: string | null) => void
}

export const useStore = create<AppState>((set, get) => ({
  token: localStorage.getItem('zeek_token'),
  userId: null,
  email: null,
  derivConnected: false,
  balance: null,
  activeSymbols: [],
  ticks: {},
  bankroll: null,
  strategies: [],
  operating: false,
  operatingPage: null,
  accounts: [],
  currentLoginid: null,
  isConnecting: false,
  error: null,

  setAuth: (token, userId, email) => {
    localStorage.setItem('zeek_token', token)
    set({ token, userId, email })
  },

  logout: () => {
    localStorage.removeItem('zeek_token')
    set({ token: null, userId: null, email: null, derivConnected: false, balance: null, ticks: {} })
  },

  setDerivStatus: (status) =>
    set({
      derivConnected: status.connected,
      balance: status.balance,
      activeSymbols: status.active_symbols,
    }),

  addTick: (symbol, tick) => {
    const ticks = { ...get().ticks }
    if (!ticks[symbol]) ticks[symbol] = []
    ticks[symbol] = [...ticks[symbol].slice(-299), tick] // keep last 300
    set({ ticks })
  },

  setBankroll: (data) => set({ bankroll: data }),
  setStrategies: (list) => set({ strategies: list }),
  setOperating: (active, pageId) => set({ operating: active, operatingPage: pageId || null }),
  setAccounts: (accounts, loginid) => set({ accounts, currentLoginid: loginid }),
  setConnecting: (v) => set({ isConnecting: v }),
  setError: (msg) => set({ error: msg }),
}))
