import { useEffect, useState } from 'react'
import { Plus, Save, Play, Trash2 } from 'lucide-react'
import { strategies as api } from '../services/api'
import { useStore } from '../store'
import { CustomStrategyBuilder } from '../components/CustomStrategyBuilder'
import { MartingaleConfig } from '../components/MartingaleConfig'

export function SetupManager() {
  const [setups, setSetups] = useState<any[]>([])
  const [editing, setEditing] = useState<any | null>(null)
  const [saving, setSaving] = useState(false)
  const refresh = useStore((s) => s.setStrategies)

  const load = async () => {
    try {
      const data = await api.list()
      setSetups(data)
      refresh(data)
    } catch { /* ignore */ }
  }

  useEffect(() => { load() }, [])

  const newSetup = () => {
    setEditing({
      name: '',
      description: '',
      pages: [],
      management: {
        initial_stake: 2.0,
        martingale_enabled: false,
        martingale_multiplier: 2.0,
        martingale_max_steps: 5,
        multiplier_enabled: false,
        multiplier_value: 2.0,
        defense_mode: 'none',
        profit_target: null,
        loss_limit: null,
      },
    })
  }

  const save = async () => {
    if (!editing) return
    setSaving(true)
    try {
      if (editing.id) {
        await api.update(editing.id, editing)
      } else {
        await api.create(editing)
      }
      setEditing(null)
      await load()
    } catch (e) {
      console.error('Save failed', e)
    } finally {
      setSaving(false)
    }
  }

  const deleteSetup = async (id: number) => {
    await api.delete(id)
    await load()
  }

  const activate = async (id: number) => {
    await api.activate(id)
  }

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-4">
      {/* List */}
      <div className="space-y-4">
        <div className="flex items-center justify-between">
          <h1 className="text-xl font-bold text-white">Setups</h1>
          <button onClick={newSetup} className="flex items-center gap-1 text-sm bg-[#f86525] hover:bg-[#e05515] text-white px-3 py-1.5 rounded-lg transition-colors">
            <Plus size={16} /> Novo
          </button>
        </div>

        <div className="space-y-2">
          {setups.map((s: any) => (
            <div key={s.id} className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
              <div className="flex items-start justify-between">
                <div>
                  <h3 className="text-sm font-semibold text-white">{s.name}</h3>
                  {s.description && <p className="text-xs text-[#6b6b80] mt-0.5">{s.description}</p>}
                  <div className="flex gap-2 mt-2">
                    <span className="text-xs text-[#5a6478]">{s.pages?.length || 0} página(s)</span>
                    <span className={`text-xs ${s.is_builtin ? 'text-[#ffd64f]' : 'text-[#6b6b80]'}`}>
                      {s.is_builtin ? 'Built-in' : 'Custom'}
                    </span>
                  </div>
                </div>
                <div className="flex gap-1">
                  <button onClick={() => setEditing(s)} className="p-1.5 text-[#6b6b80] hover:text-white transition-colors" title="Editar">
                    <Save size={14} />
                  </button>
                  <button onClick={() => activate(s.id)} className="p-1.5 text-green-400 hover:text-green-300 transition-colors" title="Ativar">
                    <Play size={14} />
                  </button>
                  <button onClick={() => deleteSetup(s.id)} className="p-1.5 text-red-400 hover:text-red-300 transition-colors" title="Deletar">
                    <Trash2 size={14} />
                  </button>
                </div>
              </div>
            </div>
          ))}
          {setups.length === 0 && (
            <p className="text-sm text-[#6b6b80] italic">Nenhum setup ainda. Crie o primeiro!</p>
          )}
        </div>
      </div>

      {/* Editor */}
      <div className="space-y-4">
        {editing ? (
          <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4 space-y-4">
            <h2 className="text-sm font-semibold text-white">{editing.id ? 'Editar' : 'Novo'} Setup</h2>

            <div>
              <label className="text-xs text-[#6b6b80]">Nome</label>
              <input
                value={editing.name}
                onChange={(e) => setEditing({ ...editing, name: e.target.value })}
                className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
              />
            </div>
            <div>
              <label className="text-xs text-[#6b6b80]">Descrição</label>
              <textarea
                value={editing.description}
                onChange={(e) => setEditing({ ...editing, description: e.target.value })}
                className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded px-3 py-2 text-sm text-white mt-1"
                rows={2}
              />
            </div>

            <CustomStrategyBuilder
              rules={editing.pages?.[0]?.rules || []}
              onChange={(rules) => {
                const pages = [{ ...(editing.pages?.[0] || {}), rules }]
                setEditing({ ...editing, pages })
              }}
              mode="AND"
              onModeChange={() => {}}
            />

            <MartingaleConfig
              enabled={editing.management?.martingale_enabled}
              multiplier={editing.management?.martingale_multiplier || 2}
              maxSteps={editing.management?.martingale_max_steps || 5}
              multEnabled={editing.management?.multiplier_enabled}
              multValue={editing.management?.multiplier_value || 2}
              onChange={(m) => setEditing({ ...editing, management: { ...editing.management, ...m } })}
            />

            <div className="flex gap-2 pt-2">
              <button onClick={save} disabled={saving} className="flex items-center gap-1 text-sm bg-[#f86525] hover:bg-[#e05515] disabled:opacity-50 text-white px-4 py-2 rounded-lg transition-colors">
                <Save size={16} /> {saving ? 'Salvando...' : 'Salvar'}
              </button>
              <button onClick={() => setEditing(null)} className="text-sm bg-[#1a1a24] text-[#6b6b80] px-4 py-2 rounded-lg hover:text-white transition-colors">
                Cancelar
              </button>
            </div>
          </div>
        ) : (
          <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-4">
            <p className="text-sm text-[#6b6b80] italic">Selecione um setup para editar ou crie um novo.</p>
          </div>
        )}
      </div>
    </div>
  )
}
