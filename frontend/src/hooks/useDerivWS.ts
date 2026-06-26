// React hook for Deriv WebSocket
import { useEffect, useRef } from 'react'
import { derivWS } from '../services/ws'
import { useStore } from '../store'
import type { WSMessage, Tick } from '../types'

export function useDerivWS() {
  const token = useStore((s) => s.token)
  const setDerivStatus = useStore((s) => s.setDerivStatus)
  const addTick = useStore((s) => s.addTick)
  const setError = useStore((s) => s.setError)

  const callbackRef = useRef<(msg: WSMessage) => void>()

  useEffect(() => {
    if (!token) return

    callbackRef.current = (msg) => {
      switch (msg.type) {
        case 'tick':
          addTick(msg.symbol, msg.tick as Tick)
          break
        case 'balance':
          setDerivStatus({ connected: true, balance: msg.balance, active_symbols: [] })
          break
        case 'deriv_status':
          setDerivStatus({ connected: msg.connected, balance: null, active_symbols: [] })
          break
        case 'status':
          setDerivStatus(msg)
          break
        case 'error':
          setError(msg.message)
          break
      }
    }

    derivWS.connect(token)
    const unsub = derivWS.subscribe(callbackRef.current)

    return () => {
      unsub()
      derivWS.disconnect()
    }
  }, [token])

  return derivWS
}
