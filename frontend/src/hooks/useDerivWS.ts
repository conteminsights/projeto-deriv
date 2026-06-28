// React hook for Deriv WebSocket
import { useEffect, useRef } from 'react'
import { derivWS } from '../services/ws'
import { useStore } from '../store'
import type { WSMessage, Tick } from '../types'

export function useDerivWS() {
  const token = useStore((s) => s.token)
  const setDerivStatus = useStore((s) => s.setDerivStatus)
  const addTick = useStore((s) => s.addTick)
  const setOperating = useStore((s) => s.setOperating)
  const setAccounts = useStore((s) => s.setAccounts)
  const setError = useStore((s) => s.setError)
  const setMiniMetaReached = useStore((s) => s.setMiniMetaReached)
  const setControlledReset = useStore((s) => s.setControlledReset)

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
        case 'operating_status':
          setOperating(msg.operating, msg.page_id)
          break
        case 'accounts':
          setAccounts(msg.accounts, msg.current_loginid)
          break
        case 'mini_meta':
          if (msg.status === 'reached') {
            setMiniMetaReached({ profit: msg.profit, active: true })
          }
          break
        case 'controlled_reset':
          setControlledReset({ reason: msg.reason, message: msg.message, active: true })
          break
        case 'controlled_reset_done':
          setControlledReset({ reason: msg.reason, message: msg.message, active: false })
          setMiniMetaReached({ profit: 0, active: false })
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
