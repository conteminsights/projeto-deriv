// Mini-meta dialog + max entries
import { useState } from 'react'
import { Target, X } from 'lucide-react'

interface Props {
  open: boolean
  onClose: () => void
  profitTarget: number
  maxEntries: number
  onSave: (profitTarget: number, maxEntries: number) => void
}

export function MiniMetaDialog({ open, onClose, profitTarget, maxEntries, onSave }: Props) {
  const [target, setTarget] = useState(profitTarget)
  const [entries, setEntries] = useState(maxEntries)

  if (!open) return null

  return (
    <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50" onClick={onClose}>
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-6 w-full max-w-sm mx-4" onClick={(e) => e.stopPropagation()}>
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Target size={18} className="text-[#f86525]" />
            <h2 className="text-sm font-semibold text-white">Mini-Meta</h2>
          </div>
          <button onClick={onClose} className="text-[#6b6b80] hover:text-white transition-colors">
            <X size={18} />
          </button>
        </div>

        <div className="space-y-4">
          <div>
            <label className="text-xs text-[#6b6b80]">Meta de Lucro ($)</label>
            <input
              type="number"
              value={target}
              onChange={(e) => setTarget(parseFloat(e.target.value) || 0)}
              min="0"
              step="5"
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
            />
            <p className="text-xs text-[#5a6478] mt-1">0 = sem limite</p>
          </div>

          <div>
            <label className="text-xs text-[#6b6b80]">Máximo de Entradas</label>
            <input
              type="number"
              value={entries}
              onChange={(e) => setEntries(parseInt(e.target.value) || 0)}
              min="0"
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
            />
            <p className="text-xs text-[#5a6478] mt-1">0 = ilimitado</p>
          </div>

          <button
            onClick={() => { onSave(target, entries); onClose() }}
            className="w-full bg-[#f86525] hover:bg-[#e05515] text-white px-4 py-2 rounded-lg text-sm transition-colors"
          >
            Salvar
          </button>
        </div>
      </div>
    </div>
  )
}
