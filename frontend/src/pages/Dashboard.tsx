export function Dashboard() {
  return (
    <div className="space-y-4">
      <h1 className="text-xl font-bold">Dashboard</h1>

      {/* Status Cards */}
      <div className="grid grid-cols-4 gap-4">
        <div className="card">
          <div className="text-sm text-zeek-text-muted">Saldo</div>
          <div className="text-2xl font-bold">—</div>
        </div>
        <div className="card">
          <div className="text-sm text-zeek-text-muted">Profit Hoje</div>
          <div className="text-2xl font-bold text-zeek-profit">$0.00</div>
        </div>
        <div className="card">
          <div className="text-sm text-zeek-text-muted">Wins / Losses</div>
          <div className="text-2xl font-bold">0 / 0</div>
        </div>
        <div className="card">
          <div className="text-sm text-zeek-text-muted">Páginas Ativas</div>
          <div className="text-2xl font-bold">0</div>
        </div>
      </div>

      {/* TODO: Implementar gráficos e cards de páginas */}
      <div className="card">
        <p className="text-zeek-text-muted text-sm">
          Conecte-se com seu token PAT da Deriv para começar a operar.
        </p>
      </div>
    </div>
  )
}
