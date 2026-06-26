import { useState } from 'react'
import { Calculator as CalcIcon, TrendingUp } from 'lucide-react'

export function Calculator() {
  const [stake, setStake] = useState(2.0)
  const [multiplier, setMultiplier] = useState(2.0)
  const [steps, setSteps] = useState(5)
  const [martingale, setMartingale] = useState(true)

  const progression = []
  if (martingale) {
    let s = stake
    for (let i = 0; i < steps; i++) {
      progression.push({ step: i + 1, value: s })
      s *= multiplier
    }
  }

  return (
    <div className="max-w-2xl space-y-4">
      <h1 className="text-xl font-bold text-white flex items-center gap-2">
        <CalcIcon size={20} className="text-[#f86525]" /> Calculadora de Multiplicador
      </h1>

      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4 space-y-4">
        <div className="grid grid-cols-3 gap-4">
          <div>
            <label className="text-xs text-[#6b6b80]">Stake Inicial ($)</label>
            <input
              type="number"
              value={stake}
              onChange={(e) => setStake(parseFloat(e.target.value) || 2)}
              min="0.5"
              step="0.5"
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-[#6b6b80]">Multiplicador</label>
            <input
              type="number"
              value={multiplier}
              onChange={(e) => setMultiplier(parseFloat(e.target.value) || 2)}
              min="1.0"
              step="0.5"
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-[#6b6b80]">Steps</label>
            <input
              type="number"
              value={steps}
              onChange={(e) => setSteps(parseInt(e.target.value) || 5)}
              min="1"
              max="20"
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
            />
          </div>
        </div>

        <label className="flex items-center gap-2 cursor-pointer">
          <input
            type="checkbox"
            checked={martingale}
            onChange={(e) => setMartingale(e.target.checked)}
            className="w-4 h-4 rounded border-[#2a2a3a] bg-[#1a1a24] text-[#f86525]"
          />
          <span className="text-sm text-white">Martingale Progressivo</span>
        </label>
      </div>

      {/* Progression */}
      {progression.length > 0 && (
        <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
          <h2 className="text-sm font-semibold text-white mb-3 flex items-center gap-2">
            <TrendingUp size={16} className="text-[#ffd64f]" /> Progressão
          </h2>
          <div className="space-y-1">
            {progression.map((p) => (
              <div key={p.step} className="flex items-center justify-between text-sm py-1.5 border-b border-[#1e1e2a] last:border-0">
                <span className="text-[#6b6b80] font-mono">Step #{p.step}</span>
                <span className="text-white font-mono font-medium">${p.value.toFixed(2)}</span>
              </div>
            ))}
          </div>
          <div className="flex items-center justify-between text-sm mt-3 pt-3 border-t border-[#1e1e2a]">
            <span className="text-[#6b6b80]">Custo total (se perder todas):</span>
            <span className="text-red-400 font-mono font-bold">
              ${progression.reduce((a, p) => a + p.value, 0).toFixed(2)}
            </span>
          </div>
          <div className="flex items-center justify-between text-sm mt-1">
            <span className="text-[#6b6b80]">Lucro se ganhar na última:</span>
            <span className="text-green-400 font-mono font-bold">
              ${(progression[progression.length - 1].value * 0.9 - progression.reduce((a, p) => a + p.value, 0)).toFixed(2)}
            </span>
          </div>
        </div>
      )}
    </div>
  )
}
