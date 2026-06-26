// Configurador visual de estratégia CUSTOM
import { Plus, Trash2 } from 'lucide-react'
import type { Rule, TriggerCondition } from '../types'

interface Props {
  rules: Rule[]
  onChange: (rules: Rule[]) => void
  mode: string
  onModeChange: (mode: string) => void
}

const INDICATORS = [
  { value: 'price', label: 'Preço' },
  { value: 'sma', label: 'SMA' },
  { value: 'ema', label: 'EMA' },
  { value: 'rsi', label: 'RSI' },
  { value: 'macd', label: 'MACD' },
  { value: 'bb', label: 'Bollinger' },
]

const OPERATORS: Record<string, { value: string; label: string }[]> = {
  price: [
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '>=', label: '>=' },
    { value: '<=', label: '<=' },
    { value: 'cross_above', label: 'Cruzou p/ cima' },
    { value: 'cross_below', label: 'Cruzou p/ baixo' },
  ],
  default: [
    { value: '>', label: '>' },
    { value: '<', label: '<' },
    { value: '>=', label: '>=' },
    { value: '<=', label: '<=' },
  ],
}

function newRule(): Rule {
  return {
    condition: { indicator: 'price', operator: '>', value: 0, timeframe: 14 },
    contract_type: 'CALL',
    duration: 1,
    duration_unit: 't',
  }
}

export function CustomStrategyBuilder({ rules, onChange, mode, onModeChange }: Props) {
  const addRule = () => onChange([...rules, newRule()])

  const updateRule = (i: number, rule: Rule) => {
    const next = [...rules]
    next[i] = rule
    onChange(next)
  }

  const removeRule = (i: number) => {
    onChange(rules.filter((_, idx) => idx !== i))
  }

  const updateCondition = (i: number, field: keyof TriggerCondition, value: any) => {
    const rule = { ...rules[i] }
    if (field === 'indicator' && value === 'price') {
      rule.condition = { ...rule.condition, indicator: value, operator: '>' }
    } else {
      rule.condition = { ...rule.condition, [field]: value }
    }
    updateRule(i, rule)
  }

  return (
    <div className="space-y-3">
      <div className="flex items-center justify-between">
        <h3 className="text-sm font-semibold text-white">Regras CUSTOM</h3>
        <button onClick={addRule} className="flex items-center gap-1 text-xs text-[#f86525] hover:text-[#ff8a50] transition-colors">
          <Plus size={14} /> Adicionar Regra
        </button>
      </div>

      {/* Mode selector */}
      <div className="flex gap-2">
        {['AND', 'OR'].map((m) => (
          <button
            key={m}
            onClick={() => onModeChange(m)}
            className={`px-3 py-1.5 rounded-lg text-xs font-mono transition-colors ${
              mode === m
                ? 'bg-[#f86525]/20 text-[#f86525] border border-[#f86525]/30'
                : 'bg-[#1a1a24] text-[#6b6b80] border border-[#2a2a3a]'
            }`}
          >
            Modo {m}
          </button>
        ))}
      </div>

      {/* Rules */}
      {rules.map((rule, i) => (
        <div key={i} className="bg-[#1a1a24] border border-[#2a2a3a] rounded-lg p-3 space-y-2">
          <div className="flex items-center justify-between">
            <span className="text-xs text-[#6b6b80] font-mono">Regra #{i + 1}</span>
            <button onClick={() => removeRule(i)} className="text-red-400 hover:text-red-300 transition-colors">
              <Trash2 size={14} />
            </button>
          </div>

          <div className="grid grid-cols-2 md:grid-cols-4 gap-2">
            <select
              value={rule.condition.indicator}
              onChange={(e) => updateCondition(i, 'indicator', e.target.value)}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
            >
              {INDICATORS.map((ind) => (
                <option key={ind.value} value={ind.value}>{ind.label}</option>
              ))}
            </select>

            <select
              value={rule.condition.operator}
              onChange={(e) => updateCondition(i, 'operator', e.target.value)}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
            >
              {(OPERATORS[rule.condition.indicator] || OPERATORS.default).map((op) => (
                <option key={op.value} value={op.value}>{op.label}</option>
              ))}
            </select>

            <input
              type="number"
              value={rule.condition.value}
              onChange={(e) => updateCondition(i, 'value', parseFloat(e.target.value) || 0)}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
              placeholder="Valor"
            />

            {(rule.condition.indicator === 'sma' || rule.condition.indicator === 'ema' || rule.condition.indicator === 'rsi') && (
              <input
                type="number"
                value={rule.condition.timeframe}
                onChange={(e) => updateCondition(i, 'timeframe', parseInt(e.target.value) || 14)}
                className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
                placeholder="Período"
              />
            )}
          </div>

          <div className="flex gap-2">
            <select
              value={rule.contract_type}
              onChange={(e) => updateRule(i, { ...rule, contract_type: e.target.value as 'CALL' | 'PUT' })}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
            >
              <option value="CALL">CALL</option>
              <option value="PUT">PUT</option>
            </select>
            <input
              type="number"
              value={rule.duration}
              onChange={(e) => updateRule(i, { ...rule, duration: parseInt(e.target.value) || 1 })}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white w-20"
              placeholder="Dur."
            />
            <select
              value={rule.duration_unit}
              onChange={(e) => updateRule(i, { ...rule, duration_unit: e.target.value })}
              className="bg-[#12121a] border border-[#2a2a3a] rounded px-2 py-1.5 text-xs text-white"
            >
              <option value="t">Ticks</option>
              <option value="m">Minutos</option>
              <option value="h">Horas</option>
            </select>
          </div>
        </div>
      ))}

      {rules.length === 0 && (
        <p className="text-xs text-[#6b6b80] italic">Nenhuma regra definida. Clique em "Adicionar Regra" para começar.</p>
      )}
    </div>
  )
}
