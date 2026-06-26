export function Login() {
  return (
    <div className="min-h-screen bg-zeek-bg flex items-center justify-center">
      <div className="card w-full max-w-md">
        {/* Logo */}
        <div className="text-center mb-8">
          <div className="font-mono text-xs text-zeek-accent">
            ███████╗███████╗███████╗██╗  ██╗<br />
            ╚══███╔╝██╔════╝██╔════╝██║ ██╔╝<br />
            █████╔╝ █████╗  █████╗  █████╔╝<br />
            ╚══██╔╝  ██╔══╝  ██╔══╝  ██╔═██╗<br />
            ███████╗███████╗██║  ██║<br />
            ╚══════╝╚══════╝╚═╝  ╚═╝
          </div>
          <h1 className="text-2xl font-bold mt-2">ZeeK.Web</h1>
          <p className="text-zeek-text-secondary text-sm">Bot de Trading para Deriv</p>
        </div>

        {/* Form */}
        <form className="space-y-4" onSubmit={e => e.preventDefault()}>
          <div>
            <label className="block text-sm text-zeek-text-secondary mb-1">Email</label>
            <input type="email" className="w-full" placeholder="seu@email.com" />
          </div>
          <div>
            <label className="block text-sm text-zeek-text-secondary mb-1">Senha</label>
            <input type="password" className="w-full" placeholder="••••••••" />
          </div>
          <button type="submit" className="btn-primary w-full">
            Entrar
          </button>
          <p className="text-center text-xs text-zeek-text-muted">
            Token da Deriv será configurado após o login
          </p>
        </form>
      </div>
    </div>
  )
}
