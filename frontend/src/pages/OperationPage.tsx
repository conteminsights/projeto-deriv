import { useState } from 'react'
import { useStore } from '../store'
import { TradeChart } from '../components/TradeChart'
import { derivWS } from '../services/ws'

export function OperationPage() {
  const ticks = useStore((s) => s.ticks)
  const derivConnected = useStore((s) => s.derivConnected)
  const operating = useStore((s) => s.operating)
  const [symbol, setSymbol] = useState('R_100')
  const [patToken, setPatToken] = useState('')
  const [selectedMarket, setSelectedMarket] = useState('R_100')

  const markets = ['R_100', 'R_75', 'R_50', 'R_25', 'R_10', '1HZ']

  const handleConnect = () => {
    if (patToken) derivWS.connectDeriv(patToken)
  }

  const handleSubscribe = (m: string) => {
    setSelectedMarket(m)
    derivWS.subscribeTicks(m)
    setSymbol(m)
  }

  const handleUnsubscribe = () => {
    derivWS.unsubscribeTicks(symbol)
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <h1 className="text-xl font-bold text-white">Operação</h1>
        <div className={`flex items-center gap-2 text-sm ${derivConnected ? 'text-green-400' : 'text-[#6b6b80]'}`}>
          <div className={`w-2 h-2 rounded-full ${derivConnected ? 'bg-green-400' : 'bg-[#6b6b80]'}`} />
          {derivConnected ? 'Conectado' : 'Desconectado'}
        </div>
      </div>

      {/* Connection */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3">Conexão Deriv</h2>
        <div className="flex gap-2">
          <input
            type="password"
            value={patToken}
            onChange={(e) => setPatToken(e.target.value)}
            placeholder="Token PAT da Deriv"
            className="flex-1 bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2 text-white text-sm placeholder-[#4a4a5a] focus:outline-none focus:border-[#f86525]"
          />
          <button
            onClick={handleConnect}
            disabled={!patToken || derivConnected}
            className="bg-[#f86525] hover:bg-[#e05515] disabled:opacity-50 text-white px-4 py-2 rounded-lg text-sm font-medium transition-colors"
          >
            Conectar
          </button>
          {derivConnected && (
            <button
              onClick={() => derivWS.disconnectDeriv()}
              className="bg-red-900/30 hover:bg-red-900/50 text-red-400 px-4 py-2 rounded-lg text-sm transition-colors"
            >
              Desconectar
            </button>
          )}
        </div>
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
          <h2 className="text-sm font-semibold text-white">Estratégia</h2>
          <div className="flex items-center gap-2">
            <span className={`text-xs ${operating ? 'text-green-400' : 'text-[#6b6b80]'}`}>
              {operating ? 'Operando' : 'Parado'}
            </span>
            <button
              onClick={() => operating ? derivWS.stopOperating() : derivWS.startOperating()}
              disabled={!derivConnected}
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
            ? 'Conecte-se à Deriv primeiro'
            : operating
              ? 'Estratégia ativa — monitorando ticks e executando ordens'
              : 'Clique em OPERAR para iniciar a estratégia CUSTOM'}
        </div>
      </div>

      {/* Controls */}
      <div className="grid grid-cols-3 gap-4">
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Stake</div>
          <div className="text-lg font-bold text-white">$2.00</div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Martingale</div>
          <div className="text-lg font-bold text-white">OFF</div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide mb-1">Defesa</div>
          <div className="text-lg font-bold text-white">—</div>
        </div>
      </div>
    </div>
  )
}
