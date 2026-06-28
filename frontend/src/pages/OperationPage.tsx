import { useState, useEffect } from 'react'
import { useStore } from '../store'
import { TradeChart } from '../components/TradeChart'
import { strategies as strategiesApi } from '../services/api'
import { derivWS } from '../services/ws'

export function OperationPage() {
  const ticks = useStore((s) => s.ticks)
  const derivConnected = useStore((s) => s.derivConnected)
  const operating = useStore((s) => s.operating)
  const bankroll = useStore((s) => s.bankroll)
  const [symbol, setSymbol] = useState('R_100')
  const [selectedMarket, setSelectedMarket] = useState('R_100')
  const [setups, setSetups] = useState<any[]>([])
  const [selectedSetupId, setSelectedSetupId] = useState<number | null>(null)
  const [loadingSetup, setLoadingSetup] = useState(false)
  const [msg, setMsg] = useState('')

  const markets = ['R_100', 'R_75', 'R_50', 'R_25', 'R_10', '1HZ']

  // Load available setups
  useEffect(() => {
    strategiesApi.list().then(setSetups).catch(() => {})
  }, [])

  const handleSubscribe = (m: string) => {
    setSelectedMarket(m)
    derivWS.subscribeTicks(m)
    setSymbol(m)
  }

  const handleUnsubscribe = () => {
    derivWS.unsubscribeTicks(symbol)
  }

  const loadAndStart = async () => {
    if (!selectedSetupId) {
      setMsg('Selecione uma estratégia primeiro')
      return
    }
    setLoadingSetup(true)
    setMsg('')
    try {
      // Load the strategy into the runner via WS
      derivWS.loadStrategy(selectedSetupId)
      setMsg('Estratégia carregada. Conectando...')
    } catch (e: any) {
      setMsg('Erro ao carregar estratégia')
    } finally {
      setLoadingSetup(false)
    }
  }

  // Auto-subscribe to selected market when starting
  const handleStart = () => {
    if (!selectedSetupId) {
      setMsg('Selecione uma estratégia primeiro')
      return
    }
    // Subscribe to market ticks
    derivWS.subscribeTicks(selectedMarket)
    // Start operating
    derivWS.startOperating('default')
    setMsg('')
  }

  const handleStop = () => {
    derivWS.stopOperating()
    setMsg('')
  }

  const selectedSetup = setups.find(s => s.id === selectedSetupId)

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Operação</h1>
        <div className={`flex items-center gap-2 text-sm ${derivConnected ? 'text-green-400' : 'text-[#6b6b80]'}`}>
          <div className={`w-2 h-2 rounded-full ${derivConnected ? 'bg-green-400' : 'bg-[#6b6b80]'}`} />
          {derivConnected ? 'Conectado' : 'Desconectado'}
        </div>
      </div>

      {/* Strategy Selector */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3">Estratégia</h2>
        <div className="flex gap-2">
          <select
            value={selectedSetupId ?? ''}
            onChange={(e) => {
              const id = e.target.value ? parseInt(e.target.value) : null
              setSelectedSetupId(id)
              setMsg('')
            }}
            className="flex-1 bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2.5 text-sm text-white focus:outline-none focus:border-[#f86525]"
          >
            <option value="">— Selecione uma estratégia —</option>
            {setups.map((s) => (
              <option key={s.id} value={s.id}>{s.name}</option>
            ))}
          </select>
          <button
            onClick={loadAndStart}
            disabled={!selectedSetupId || loadingSetup}
            className="bg-[#1a1a24] border border-[#2a2a3a] text-white px-4 py-2 rounded-lg text-sm hover:border-[#f86525]/30 disabled:opacity-50 transition-colors"
          >
            {loadingSetup ? 'Carregando...' : 'Carregar'}
          </button>
        </div>

        {/* Selected strategy details */}
        {selectedSetup && (
          <div className="mt-3 bg-[#1a1a24] rounded-lg p-3 text-xs">
            <div className="text-[#6b6b80] mb-1">
              {selectedSetup.pages?.[0]?.rules?.length || 0} regra(s) · 
              Mercado: {selectedSetup.pages?.[0]?.market || 'R_100'} ·
              Modo: {selectedSetup.pages?.[0]?.mode || 'CALL_PUT'}
            </div>
            {selectedSetup.description && (
              <div className="text-[#5a6478]">{selectedSetup.description}</div>
            )}
          </div>
        )}

        {msg && (
          <div className="mt-2 bg-[#f86525]/10 border border-[#f86525]/20 rounded-lg px-3 py-2 text-xs text-[#f86525]">
            {msg}
          </div>
        )}
      </div>

      {/* Markets */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3">Mercados</h2>
        <div className="flex flex-wrap gap-2">
          {markets.map((m) => (
            <button
              key={m}
              onClick={() => handleSubscribe(m)}
              className={`px-3 py-1.5 rounded-lg text-sm font-mono transition-colors ${
                selectedMarket === m
                  ? 'bg-[#f86525]/20 text-[#f86525] border border-[#f86525]/30'
                  : 'bg-[#1a1a24] text-[#6b6b80] border border-[#2a2a3a] hover:border-[#f86525]/30'
              }`}
            >
              {m}
            </button>
          ))}
          {ticks[symbol] && ticks[symbol].length > 0 && (
            <button
              onClick={handleUnsubscribe}
              className="px-3 py-1.5 rounded-lg text-sm bg-red-900/20 text-red-400 border border-red-800/30 hover:border-red-500/50 transition-colors"
            >
              Sair {symbol}
            </button>
          )}
        </div>
      </div>

      {/* Chart */}
      <TradeChart
        ticks={ticks[selectedMarket] || []}
        symbol={selectedMarket}
        showSMA={true}
      />

      {/* Operating Controls */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <div className="flex items-center justify-between mb-3">
          <h2 className="text-sm font-semibold text-white">Controles</h2>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${operating ? 'text-green-400' : 'text-[#6b6b80]'}`}>
              {operating ? 'Operando' : 'Parado'}
            </span>
            <button
              onClick={operating ? handleStop : handleStart}
              disabled={!derivConnected || !selectedSetupId}
              className={`px-4 py-1.5 rounded-lg text-sm font-medium transition-colors ${
                operating
                  ? 'bg-red-900/30 text-red-400 hover:bg-red-900/50 border border-red-800/30'
                  : 'bg-green-900/30 text-green-400 hover:bg-green-900/50 border border-green-800/30'
              } disabled:opacity-50 disabled:cursor-not-allowed`}
            >
              {operating ? 'PARAR' : 'OPERAR'}
            </button>
          </div>
        </div>
        <div className="text-xs text-[#6b6b80]">
          {!derivConnected
            ? 'Conecte-se à Deriv primeiro (Config → Token PAT)'
            : !selectedSetupId
              ? 'Selecione uma estratégia acima'
              : operating
                ? 'Estratégia ativa — monitorando ticks e executando ordens'
                : 'Clique em OPERAR para iniciar'}
        </div>
      </div>

      {/* Stats */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Stake</div>
          <div className="text-lg font-bold text-white">
            ${bankroll?.state?.current_stake?.toFixed(2) || '2.00'}
          </div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Profit</div>
          <div className={`text-lg font-bold ${(bankroll?.state?.session_profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            ${bankroll?.state?.session_profit?.toFixed(2) || '0.00'}
          </div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Entradas</div>
          <div className="text-lg font-bold text-white">{bankroll?.state?.session_entries || 0}</div>
        </div>
      </div>
    </div>
  )
}
