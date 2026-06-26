import { useState } from 'react'
import { BarChart3, TrendingUp, TrendingDown } from 'lucide-react'

const MARKETS = ['R_100', 'R_75', 'R_50', 'R_25', 'R_10', '1HZ']

// Simple pattern detection simulation
function analyze(_symbol: string) {
  const patterns = [
    { name: 'Tendência de Alta', confidence: Math.random() * 0.6 + 0.2, direction: 'up' },
    { name: 'Tendência de Baixa', confidence: Math.random() * 0.6 + 0.2, direction: 'down' },
    { name: 'Range Lateral', confidence: Math.random() * 0.5 + 0.1, direction: 'side' },
    { name: 'Suporte testado', confidence: Math.random() * 0.7 + 0.1, direction: 'up' },
    { name: 'Resistência testada', confidence: Math.random() * 0.7 + 0.1, direction: 'down' },
  ]
  return patterns.sort((a, b) => b.confidence - a.confidence).slice(0, 3)
}

export function PatternAnalysis() {
  const [selectedMarket, setSelectedMarket] = useState('R_100')
  const [results, setResults] = useState<any[]>([])

  const runAnalysis = () => {
    setResults(analyze(selectedMarket))
  }

  const confidenceColor = (v: number) => {
    if (v >= 0.6) return 'text-green-400'
    if (v >= 0.3) return 'text-[#ffd64f]'
    return 'text-[#6b6b80]'
  }

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-xl font-bold text-white flex items-center gap-2">
        <BarChart3 size={20} className="text-[#f86525]" /> Análise de Padrões
      </h1>

      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
        <div className="flex gap-2 mb-4">
          {MARKETS.map((m) => (
            <button
              key={m}
              onClick={() => setSelectedMarket(m)}
              className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
                selectedMarket === m
                  ? 'bg-[#f86525]/20 text-[#f86525] border border-[#f86525]/30'
                  : 'bg-[#1a1a24] text-[#6b6b80] border border-[#2a2a3a]'
              }`}
            >
              {m}
            </button>
          ))}
        </div>
        <button onClick={runAnalysis} className="bg-[#f86525] hover:bg-[#e05515] text-white px-4 py-2 rounded-lg text-sm transition-colors">
          Analisar {selectedMarket}
        </button>
      </div>

      {results.length > 0 && (
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4 space-y-3">
          <h2 className="text-sm font-semibold text-white">Resultados para {selectedMarket}</h2>
          {results.map((r, i) => (
            <div key={i} className="flex items-center justify-between py-2 border-b border-[#1e1e2a] last:border-0">
              <div className="flex items-center gap-2">
                {r.direction === 'up' ? (
                  <TrendingUp size={16} className="text-green-400" />
                ) : r.direction === 'down' ? (
                  <TrendingDown size={16} className="text-red-400" />
                ) : (
                  <BarChart3 size={16} className="text-[#6b6b80]" />
                )}
                <span className="text-sm text-white">{r.name}</span>
              </div>
              <span className={`text-sm font-mono ${confidenceColor(r.confidence)}`}>
                {(r.confidence * 100).toFixed(0)}%
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}
