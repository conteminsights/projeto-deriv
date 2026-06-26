import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { auth } from '../services/api'
import { useStore } from '../store'

export function Login() {
  const [email, setEmail] = useState('')
  const [password, setPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const setAuth = useStore((s) => s.setAuth)
  const navigate = useNavigate()

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    setLoading(true)
    setError('')
    try {
      const res = await auth.login(email, password)
      setAuth(res.access_token, res.user_id, res.email)
      navigate('/dashboard')
    } catch (err: any) {
      setError(err.response?.data?.detail || 'Erro ao conectar')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="min-h-screen bg-[#0a0a0f] flex items-center justify-center p-4">
      <div className="bg-[#12121a] border border-[#1e1e2a] rounded-xl p-8 w-full max-w-md">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold tracking-tight">
            <span className="text-[#f86525]">ZeeK</span>
            <span className="text-white">.Web</span>
          </h1>
          <p className="text-[#6b6b80] text-sm mt-1">Bot de Trading para Deriv</p>
        </div>

        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm text-[#6b6b80] mb-1">Email</label>
            <input
              type="email"
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2.5 text-white placeholder-[#4a4a5a] focus:outline-none focus:border-[#f86525] transition-colors"
              placeholder="seu@email.com"
              required
            />
          </div>
          <div>
            <label className="block text-sm text-[#6b6b80] mb-1">Senha</label>
            <input
              type="password"
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              className="w-full bg-[#1a1a24] border border-[#2a2a3a] rounded-lg px-4 py-2.5 text-white placeholder-[#4a4a5a] focus:outline-none focus:border-[#f86525] transition-colors"
              placeholder="••••••••"
              required
            />
          </div>

          {error && (
            <div className="bg-red-900/20 border border-red-800/30 rounded-lg px-4 py-2 text-red-400 text-sm">
              {error}
            </div>
          )}

          <button
            type="submit"
            disabled={loading}
            className="w-full bg-[#f86525] hover:bg-[#e05515] disabled:opacity-50 text-white font-medium rounded-lg px-4 py-2.5 transition-colors"
          >
            {loading ? 'Conectando...' : 'Entrar'}
          </button>
        </form>

        <p className="text-center text-xs text-[#4a4a5a] mt-6">
          Token PAT da Deriv configurado após o login
        </p>
      </div>
    </div>
  )
}
