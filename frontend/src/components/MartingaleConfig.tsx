// Configuração de Martingale + Multiplicador
interface Props {
  enabled: boolean
  multiplier: number
  maxSteps: number
  multEnabled: boolean
  multValue: number
  onChange: (data: {
    martingale_enabled: boolean
    martingale_multiplier: number
    martingale_max_steps: number
    multiplier_enabled: boolean
    multiplier_value: number
  }) => void
}

export function MartingaleConfig({ enabled, multiplier, maxSteps, multEnabled, multValue, onChange }: Props) {
  return (
    <div className="space-y-3">
      <h3 className="text-sm font-semibold text-white">Gestão de Stake</h3>

      {/* Martingale */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={enabled}
          onChange={(e) => onChange({
            martingale_enabled: e.target.checked, martingale_multiplier: multiplier,
            martingale_max_steps: maxSteps, multiplier_enabled: multEnabled, multiplier_value: multValue,
          })}
          className="w-4 h-4 rounded border-[#2a2a3a] bg-[#1a1a24] text-[#f86525]"
        />
        <span className="text-sm text-white">Martingale</span>
      </label>

      {enabled && (
        <div className="grid grid-cols-2 gap-2 ml-6">
          <div>
            <label className="text-xs text-[#6b6b80]">Multiplicador</label>
            <input
              type="number"
              value={multiplier}
              onChange={(e) => onChange({
                martingale_enabled: enabled, martingale_multiplier: parseFloat(e.target.value) || 2,
                martingale_max_steps: maxSteps, multiplier_enabled: multEnabled, multiplier_value: multValue,
              })}
              step="0.5"
              min="1.0"
              className="w-full bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white mt-1"
            />
          </div>
          <div>
            <label className="text-xs text-[#6b6b80]">Max Steps</label>
            <input
              type="number"
              value={maxSteps}
              onChange={(e) => onChange({
                martingale_enabled: enabled, martingale_multiplier: multiplier,
                martingale_max_steps: parseInt(e.target.value) || 5,
                multiplier_enabled: multEnabled, multiplier_value: multValue,
              })}
              min="1"
              className="w-full bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white mt-1"
            />
          </div>
        </div>
      )}

      {/* Multiplicador */}
      <label className="flex items-center gap-2 cursor-pointer">
        <input
          type="checkbox"
          checked={multEnabled}
          onChange={(e) => onChange({
            martingale_enabled: enabled, martingale_multiplier: multiplier,
            martingale_max_steps: maxSteps, multiplier_enabled: e.target.checked, multiplier_value: multValue,
          })}
          className="w-4 h-4 rounded border-[#2a2a3a] bg-[#1a1a24] text-[#f86525]"
        />
        <span className="text-sm text-white">Multiplicador Fixo</span>
      </label>

      {multEnabled && (
        <div className="ml-6">
          <input
            type="number"
            value={multValue}
            onChange={(e) => onChange({
              martingale_enabled: enabled, martingale_multiplier: multiplier,
              martingale_max_steps: maxSteps, multiplier_enabled: multEnabled, multiplier_value: parseFloat(e.target.value) || 2,
            })}
            step="0.1"
            min="1.0"
            className="w-full bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
          />
        </div>
      )}
    </div>
  )
}
