# 09 — Deploy e Infraestrutura

---

## 9.1 Docker Compose (Desenvolvimento)

```yaml
# docker-compose.yml
version: '3.8'

services:
  backend:
    build:
      context: ./backend
      dockerfile: Dockerfile
    ports:
      - "8000:8000"
    env_file: .env
    volumes:
      - ./backend:/app
      - zeek_data:/app/data
    depends_on:
      - redis
    command: uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload

  frontend:
    build:
      context: ./frontend
      dockerfile: Dockerfile
    ports:
      - "5173:5173"
    volumes:
      - ./frontend:/app
    depends_on:
      - backend
    command: npm run dev -- --host

  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"

volumes:
  zeek_data:
```

## 9.2 Dockerfiles

### Backend
```dockerfile
# backend/Dockerfile
FROM python:3.12-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc libpq-dev && \
    rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend
```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS build

WORKDIR /app
COPY package.json package-lock.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM nginx:alpine
COPY --from=build /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 9.3 Deploy em Produção

### Opção 1: VPS (DigitalOcean, Hetzner, etc.)

```bash
# 1. Instalar Docker + Docker Compose
curl -fsSL https://get.docker.com | bash

# 2. Clonar projeto
git clone https://github.com/seu-user/zeek-web.git
cd zeek-web

# 3. Configurar variáveis
cp .env.example .env
nano .env  # Ajustar SECRET_KEY, DATABASE_URL, etc.

# 4. Subir
docker compose -f docker-compose.prod.yml up -d

# 5. Configurar Nginx (SSL)
# Usar Certbot para HTTPS
```

### Opção 2: Serviços Gerenciados

| Serviço | Para |
|---------|------|
| **Railway / Render** | Backend FastAPI |
| **Vercel / Netlify** | Frontend React |
| **Upstash** | Redis |
| **Neon / Supabase** | PostgreSQL |
| **Cloudflare** | DNS + DDoS |

### Opção 3: Kubernetes (Escalável)
```yaml
# k8s/deployment.yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: zeek-backend
spec:
  replicas: 2
  selector:
    matchLabels:
      app: zeek-backend
  template:
    metadata:
      labels:
        app: zeek-backend
    spec:
      containers:
      - name: backend
        image: zeek-web/backend:latest
        env:
        - name: DATABASE_URL
          valueFrom:
            secretKeyRef:
              name: zeek-secrets
              key: database-url
        ports:
        - containerPort: 8000
```

---

## 9.4 Variáveis de Ambiente (Produção)

```env
# Obrigatórias
SECRET_KEY=<gerar_hash_256bits_aleatorio>
DATABASE_URL=postgresql+asyncpg://user:pass@host:5432/zeek

# Opcionais
REDIS_URL=redis://redis:6379
DERIV_APP_ID=24332
CORS_ORIGINS=https://zeek.seusite.com
MONITOR_ENABLED=false

# Email (para recuperação de senha)
SMTP_HOST=
SMTP_PORT=587
SMTP_USER=
SMTP_PASS=
```

---

## 9.5 Monitoramento

### Logs
```bash
# Docker
docker compose logs -f backend

# Aplicação
# Logs em JSON estruturado para ELK/Grafana
```

### Métricas
- **Health check:** `GET /health` → `{"status": "ok"}`
- **Prometheus:** `/metrics` (com `prometheus-client`)
- **Grafana:** Dashboard com:
  - Conexões ativas
  - Trades por minuto
  - Win rate
  - Latência Deriv
  - Erros

### Alertas
- Conexão Deriv caiu por > 5min
- Taxa de erro > 5% nas últimas 100 ordens
- Saldo do usuário abaixo de $10
- Licença próxima do vencimento

---

## 9.6 Backup

```bash
# Backup do banco SQLite
cp zeek.db zeek.db.backup.$(date +%Y%m%d)

# Backup PostgreSQL
pg_dump -U user zeek > zeek_backup_$(date +%Y%m%d).sql

# Automatizar com cron
0 3 * * * /usr/local/bin/backup-zeek.sh
```

---

## 9.7 Segurança em Produção

### Checklist
- [x] HTTPS obrigatório (Certbot / Cloudflare)
- [x] SECRET_KEY forte (32+ bytes, gerada com `openssl rand -hex 32`)
- [x] CORS restrito ao domínio do frontend
- [x] Rate limiting nas rotas de API
- [x] Tokens PAT armazenados criptografados
- [x] Senhas com bcrypt (cost 12+)
- [x] JWT com expiry curto (15min) + refresh token
- [x] Docker rodando como usuário não-root
- [x] Health check sem informações sensíveis
- [x] Logs sem dados sensíveis (tokens, senhas)
