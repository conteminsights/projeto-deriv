import { useEffect } from 'react'
import { useStore } from '../store'
import { status as statusApi } from '../services/api'

export function Dashboard() {
  const derivConnected = useStore((s) => s.derivConnected)
  const balance = useStore((s) => s.balance)
  const bankroll = useStore((s) => s.bankroll)
  const ticks = useStore((s) => s.ticks)
  const setBankroll = useStore((s) => s.setBankroll)

  useEffect(() => {
    statusApi.get().then((data) => {
      console.log('Status:', data)
    })
    // Load bankroll
    import('../services/api').then(({ bankroll }) =>
      bankroll.get().then(setBankroll)
    )
  }, [])

  const totalTicks = Object.values(ticks).reduce((a, t) => a + t.length, 0)
  const profit = bankroll?.state?.session_profit ?? 0

  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold text-white">Dashboard</h1>

      {/* Status Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide">Deriv</div>
          <div className={`text-lg font-bold mt-1 ${derivConnected ? 'text-green-400' : 'text-[#6b6b80]'}`}>
            {derivConnected ? 'Conectado' : 'Offline'}
          </div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide">Saldo</div>
          <div className="text-lg font-bold text-white mt-1">
            {balance ? `$${balance.balance.toFixed(2)}` : '—'}
          </div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide">Profit Sessão</div>
          <div className={`text-lg font-bold mt-1 ${profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
            {profit >= 0 ? '+' : ''}${profit.toFixed(2)}
          </div>
        </div>
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <div className="text-xs text-[#6b6b80] uppercase tracking-wide">Ticks</div>
          <div className="text-lg font-bold text-white mt-1">{totalTicks}</div>
        </div>
      </div>

      {/* Active Markets */}
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <h2 className="text-sm font-semibold text-white mb-3">Mercados Ativos</h2>
        {Object.keys(ticks).length === 0 ? (
          <p className="text-sm text-[#6b6b80]">
            Conecte-se com seu token PAT para começar.
          </p>
        ) : (
          <div className="space-y-2">
            {Object.entries(ticks).map(([symbol, symbolTicks]) => (
              <div key={symbol} className="flex items-center justify-between text-sm">
                <span className="text-white font-mono">{symbol}</span>
                <span className="text-[#6b6b80]">
                  {symbolTicks.length} ticks · 
                  Último: ${symbolTicks[symbolTicks.length - 1]?.quote?.toFixed(5) ?? '—'}
                </span>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  )
}
