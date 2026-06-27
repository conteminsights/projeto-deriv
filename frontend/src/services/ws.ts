// WebSocket service for real-time Deriv data
import type { WSMessage } from '../types'

type WSCallback = (msg: WSMessage) => void

class DerivWebSocket {
  private ws: WebSocket | null = null
  private token: string = ''
  private listeners: Set<WSCallback> = new Set()
  private reconnectTimer: ReturnType<typeof setTimeout> | null = null

  connect(token: string) {
    this.token = token
    this._connect()
  }

  private _connect() {
    if (this.ws) return

    const url = `ws://localhost:8001/api/ws/?token=${this.token}`
    this.ws = new WebSocket(url)

    this.ws.onopen = () => {
      console.log('[WS] Connected')
      this.getStatus()
    }

    this.ws.onmessage = (event) => {
      try {
        const msg: WSMessage = JSON.parse(event.data)
        this.listeners.forEach((cb) => cb(msg))
      } catch (e) {
        console.error('[WS] Parse error:', e)
      }
    }

    this.ws.onclose = () => {
      console.log('[WS] Disconnected')
      this.ws = null
      // Auto-reconnect after 3s
      this.reconnectTimer = setTimeout(() => this._connect(), 3000)
    }

    this.ws.onerror = () => {
      this.ws?.close()
    }
  }

  disconnect() {
    if (this.reconnectTimer) clearTimeout(this.reconnectTimer)
    if (this.ws) {
      this.ws.close()
      this.ws = null
    }
  }

  subscribe(callback: WSCallback) {
    this.listeners.add(callback)
    return () => this.listeners.delete(callback)
  }

  send(action: string, payload: Record<string, any> = {}) {
    if (this.ws?.readyState === WebSocket.OPEN) {
      this.ws.send(JSON.stringify({ action, ...payload }))
    }
  }

  getStatus() {
    this.send('get_status')
  }

  subscribeTicks(symbol: string) {
    this.send('subscribe_ticks', { symbol })
  }

  unsubscribeTicks(symbol: string) {
    this.send('unsubscribe_ticks', { symbol })
  }

  connectDeriv(patToken: string) {
    this.send('connect_deriv', { pat_token: patToken })
  }

  disconnectDeriv() {
    this.send('disconnect_deriv')
  }

  startOperating(pageId: string = 'default') {
    this.send('start_operating', { page_id: pageId })
  }

  stopOperating() {
    this.send('stop_operating')
  }

  sellContract(contractId: string, price: number) {
    this.send('sell_contract', { contract_id: contractId, price })
  }

  cancelContract(contractId: string) {
    this.send('cancel_contract', { contract_id: contractId })
  }

  getAccounts() {
    this.send('get_accounts')
  }

  switchAccount(loginid: string) {
    this.send('switch_account', { loginid })
  }
}

export const derivWS = new DerivWebSocket()
