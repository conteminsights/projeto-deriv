export function TopBar() {
  return (
    <header className="h-14 bg-zeek-bg-secondary border-b border-zeek-border flex items-center px-4 gap-6">
      {/* Conexão */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-zeek-text-muted">Conexão:</span>
        <span className="text-zeek-text-muted">—</span>
      </div>

      {/* Saldo */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-zeek-text-muted">Saldo:</span>
        <span className="text-zeek-text font-semibold">—</span>
      </div>

      {/* Profit */}
      <div className="flex items-center gap-2 text-sm">
        <span className="text-zeek-text-muted">Profit:</span>
        <span className="text-zeek-text">$0.00</span>
      </div>

      {/* Ping */}
      <div className="flex items-center gap-2 text-sm ml-auto">
        <span className="text-zeek-text-muted">Ping:</span>
        <span className="text-zeek-text">—</span>
      </div>
    </header>
  )
}
