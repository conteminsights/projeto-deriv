import { useState } from 'react'
import { Save, Key, RefreshCw } from 'lucide-react'
import { tokens, bankroll as bankrollApi } from '../services/api'
import { useStore } from '../store'
import { derivWS } from '../services/ws'

export function Settings() {
  const [patToken, setPatToken] = useState('')
  const [saving, setSaving] = useState(false)
  const [loading, setLoading] = useState(false)
  const [msg, setMsg] = useState('')
  const bankroll = useStore((s) => s.bankroll)
  const derivConnected = useStore((s) => s.derivConnected)

  const saveToken = async () => {
    const token = patToken.trim()
    if (!token) return
    setSaving(true)
    try {
      await tokens.create(token, 'default')
      setMsg('Token salvo! Conectando...')
      derivWS.connectDeriv(token)
      setPatToken('')
    } catch (e: any) {
      setMsg(e.response?.data?.detail || 'Erro ao salvar token')
    } finally {
      setSaving(false)
    }
  }

  const connectDeriv = async () => {
    setLoading(true)
    try {
      const token = patToken.trim()
      if (!token) {
        setMsg('Digite o token PAT no campo acima e clique em Salvar')
        setLoading(false)
        return
      }
      derivWS.connectDeriv(token)
      setMsg('Conectando à Deriv...')
    } finally {
      setLoading(false)
    }
  }

  const resetBankroll = async () => {
    await bankrollApi.reset()
    setMsg('Banca reiniciada')
  }

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-xl font-bold text-white">Configurações</h1>

      {/* Connection Status */}
      <div className="flex items-center gap-2 text-sm mb-3">
        <span className={`w-2.5 h-2.5 rounded-full ${derivConnected ? 'bg-green-400' : 'bg-[#4a4a5a]'}`} />
        <span className={derivConnected ? 'text-green-400' : 'text-[#6b6b80]'}>
          {derivConnected ? 'Conectado à Deriv' : 'Desconectado'}
        </span>
      </div>

      {/* Token PAT */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
          <Key size={16} className="text-[#f86525]" /> Token PAT da Deriv
        </h2>
        <div className="flex gap-2">
          <input
            type="password"
            value={patToken}
            onChange={(e) => setPatToken(e.target.value)}
            placeholder="Seu token PAT da plataforma Deriv"
            className="flex-1 bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2.5 text-sm text-white placeholder-[#4a4a5a] focus:outline-none focus:border-[#f86525]"
          />
          <button onClick={saveToken} disabled={saving || !patToken} className="bg-[#f86525] hover:bg-[#e05515] disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm transition-colors">
            <Save size={16} />
          </button>
          <button onClick={connectDeriv} disabled={loading || !patToken} className="bg-[#1a1a24] border border-[#2a2a3a] text-white px-4 py-2 rounded-lg text-sm hover:border-[#f86525]/30 transition-colors">
            Conectar
          </button>
        </div>
      </div>

      {/* Bankroll */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3">Banca</h2>
        <div className="grid grid-cols-2 gap-4 text-sm">
          <div>
            <span className="text-[#6b6b80]">Stake inicial:</span>
            <span className="text-white ml-2">${bankroll?.config?.initial_stake || '2.00'}</span>
          </div>
          <div>
            <span className="text-[#6b6b80]">Stake atual:</span>
            <span className="text-white ml-2">${bankroll?.state?.current_stake || '2.00'}</span>
          </div>
          <div>
            <span className="text-[#6b6b80]">Profit sessão:</span>
            <span className={`ml-2 ${(bankroll?.state?.session_profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
              ${bankroll?.state?.session_profit?.toFixed(2) || '0.00'}
            </span>
          </div>
          <div>
            <span className="text-[#6b6b80]">Entradas:</span>
            <span className="text-white ml-2">{bankroll?.state?.session_entries || 0}</span>
          </div>
        </div>
        <button onClick={resetBankroll} className="flex items-center gap-1 text-xs text-[#6b6b80] hover:text-white mt-3 transition-colors">
          <RefreshCw size={12} /> Reiniciar Sessão
        </button>
      </div>

      {/* Message */}
      {msg && (
        <div className="bg-[#f86525]/10 border border-[#f86525]/20 rounded-lg px-4 py-2 text-sm text-[#f86525]">
          {msg}
        </div>
      )}
    </div>
  )
}
