// Configuração de defesa (BARREIRA / SOROS)
interface Props {
  mode: string
  barrier: number
  onChange: (mode: string, barrier: number) => void
}

export function DefenseConfig({ mode, barrier, onChange }: Props) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-white">Defesa</h3>

      <div className="flex flex-wrap gap-2">
        {[
          { value: 'none', label: 'Nenhuma' },
          { value: 'barrier', label: 'BARREIRA' },
          { value: 'soros_master', label: 'SOROS MASTER' },
          { value: 'soros_slave', label: 'SOROS SLAVE' },
        ].map((opt) => (
          <button
            key={opt.value}
            onClick={() => onChange(opt.value, barrier)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
              mode === opt.value
                ? 'bg-[#f86525]/20 text-[#f86525] border border-[#f86525]/30'
                : 'bg-[#1a1a24] text-[#6b6b80] border border-[#2a2a3a] hover:border-[#f86525]/30'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {(mode === 'barrier' || mode === 'soros_slave') && (
        <div className="flex items-center gap-2">
          <span className="text-xs text-[#6b6b80]">Perdas consecutivas para ativar:</span>
          <input
            type="number"
            value={barrier}
            onChange={(e) => onChange(mode, parseInt(e.target.value) || 3)}
            min="1"
            className="w-20 bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
          />
        </div>
      )}
    </div>
  )
}
