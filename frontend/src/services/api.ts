// Serviço REST API para o backend ZeeK.Web
import axios from 'axios'

const api = axios.create({
  baseURL: 'http://localhost:8001/api',
  headers: { 'Content-Type': 'application/json' },
})

// Token interceptor
api.interceptors.request.use((config) => {
  const token = localStorage.getItem('zeek_token')
  if (token) {
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

// Response error handler
api.interceptors.response.use(
  (r) => r,
  (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('zeek_token')
      window.location.href = '/login'
    }
    return Promise.reject(err)
  }
)

// ─── Auth ──────────────────────────
export const auth = {
  login: (email: string, password: string) =>
    api.post('/auth/login', null, { params: { email, password } }).then((r) => r.data),

  register: (email: string, password: string) =>
    api.post('/auth/register', null, { params: { email, password } }).then((r) => r.data),
}

// ─── Tokens ────────────────────────
export const tokens = {
  list: () => api.get('/tokens/').then((r) => r.data),
  create: (tokenValue: string, label: string = 'default') =>
    api.post('/tokens/', null, { params: { token_value: tokenValue, label } }).then((r) => r.data),
  delete: (id: number) => api.delete(`/tokens/${id}`).then((r) => r.data),
}

// ─── Strategies ────────────────────
export const strategies = {
  list: () => api.get('/strategies/').then((r) => r.data),
  get: (id: number) => api.get(`/strategies/${id}`).then((r) => r.data),
  create: (data: any) => api.post('/strategies/', data).then((r) => r.data),
  update: (id: number, data: any) => api.put(`/strategies/${id}`, data).then((r) => r.data),
  delete: (id: number) => api.delete(`/strategies/${id}`).then((r) => r.data),
  activate: (id: number) => api.post(`/strategies/${id}/activate`).then((r) => r.data),
  stop: () => api.post('/strategies/stop').then((r) => r.data),
}

// ─── Bankroll ──────────────────────
export const bankroll = {
  get: () => api.get('/bankroll/').then((r) => r.data),
  update: (data: any) => api.put('/bankroll/config', data).then((r) => r.data),
  reset: () => api.post('/bankroll/reset').then((r) => r.data),
  stop: () => api.post('/bankroll/stop').then((r) => r.data),
  getDefense: (pageId: string) => api.get(`/bankroll/defense/${pageId}`).then((r) => r.data),
  updateDefense: (pageId: string, data: any) =>
    api.put(`/bankroll/defense/${pageId}`, data).then((r) => r.data),
}

// ─── Status ────────────────────────
export const status = {
  get: () => api.get('/status/').then((r) => r.data),
}

export default api
