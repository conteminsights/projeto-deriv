# 00 — Resumo Executivo

## Projeto
**ZeeK.Web** — Versão web do ZeeK.Bot 3.1, um bot de trading para a plataforma Deriv (opções binárias CALL/PUT).

## Stack
- **Backend:** Python FastAPI + WebSockets
- **Frontend:** React + TypeScript + TailwindCSS
- **Tempo Real:** WebSocket bidirecional (ticks, ordens, status)
- **Infra:** Docker Compose

## Funcionalidades (mesmas do ZeeK.Bot original)
- Conexão WebSocket com a Deriv (wss://ws.derivws.com)
- Múltiplas páginas de operação simultâneas
- Estratégia CUSTOM com gatilhos baseados em indicadores (SMA, EMA, RSI, MACD, BB)
- Martingale com progressão de stake
- Sistema Soros (MASTER/SLAVE)
- Gestão de banca (mini-meta, mxm entradas, ajustável ao lucro)
- Limites globais de lucro/prejuízo
- Análise de padrões em ticks históricos
- Setups salvos (estratégias completas)

## Status
✅ Análise completa do ZeeK.Bot original (engenharia reversa)
✅ Documentação completa do projeto
✅ Plano de implementação em 7 fases (~34 dias)
✅ Scaffold do backend + frontend com código inicial
✅ Docker Compose para desenvolvimento

## Próximos Passos
Iniciar **Fase 1** do plano de implementação (ver `06-plano-de-implementacao.md`).
