# 03 — Integração com a API da Deriv

> Baseado na engenharia reversa do ZeeK.Bot 3.1  
> Documentação oficial da Deriv: https://developers.deriv.com/

---

## 3.1 Conexão WebSocket

### Endpoint
```
wss://ws.derivws.com/websockets/v3?app_id=24332
```

O App ID `24332` é o usado pelo ZeeK.Bot. Você pode criar o seu próprio em:
https://app.deriv.com/account/api-token

### Handshake
A conexão é WebSocket padrão (sem subprotocolo especial).

---

## 3.2 Fluxo de Mensagens

### 3.2.1 Autorização
```json
// Enviar:
{"authorize": "seu_token_pat_aqui"}

// Resposta (simplificada):
{
  "authorize": {
    "loginid": "CR1234567",
    "currency": "USD",
    "balance": 1000.00,
    "account_list": [
      {"loginid": "CR1234567", "currency": "USD", "is_virtual": false},
      {"loginid": "VRTC1234567", "currency": "USD", "is_virtual": true}
    ],
    "email": "user@example.com",
    "fullname": "User Name",
    "scopes": ["read", "trade", "payments"]
  }
}
```

### 3.2.2 Inscrever em Ticks
```json
// Enviar:
{"subscribe": 1, "ticks": "R_100"}

// Resposta inicial:
{
  "subscription": {"id": "uuid-abc-123"},
  "ticks": {
    "epoch": 1234567890,
    "quote": 1234.56,
    "symbol": "R_100"
  }
}

// Ticks subsequentes:
{
  "ticks": {
    "epoch": 1234567891,
    "quote": 1234.78,
    "symbol": "R_100"
  }
}
```

### 3.2.3 Inscrever em Balance
```json
// Enviar:
{"subscribe": 1, "balance": 1}

// Atualizações:
{
  "balance": {
    "balance": 1050.00,
    "currency": "USD",
    "loginid": "CR1234567"
  }
}
```

### 3.2.4 Inscrever em Transaction
```json
// Enviar:
{"subscribe": 1, "transaction": 1}

// Notificações de trade:
{
  "transaction": {
    "id": "contract-id-123",
    "action": "BUY",
    "amount": 10.00,
    "currency": "USD",
    "date": "2026-06-26 12:00:00"
  }
}
```

### 3.2.5 Solicitar Proposal (Cotação)
```json
// Enviar:
{
  "proposal": 1,
  "amount": 10,
  "basis": "stake",
  "contract_type": "CALL",
  "currency": "USD",
  "duration": 1,
  "duration_unit": "t",
  "symbol": "R_100"
}

// Resposta:
{
  "proposal": {
    "ask_price": 9.85,
    "payout": 19.70,
    "spot_time": 1234567890,
    "longcode": "Win payout if ...",
    "id": "proposal-uuid"
  }
}
// Em caso de erro:
{
  "proposal": {
    "error": {
      "code": "ProposalValidation",
      "message": "Contract type not available"
    }
  }
}
```

### 3.2.6 Comprar Contrato (Buy)
```json
// Enviar:
{
  "buy": "proposal-uuid",
  "price": 9.85
}

// Resposta:
{
  "buy": {
    "contract_id": 123456789,
    "balance_after": 990.15,
    "transaction_id": 987654321,
    "start_time": 1234567890,
    "purchase_time": 1234567890
  }
}
```

### 3.2.7 Monitorar Contrato
```json
// Enviar:
{"subscribe": 1, "proposal_open_contract": 1}

// Atualizações:
{
  "proposal_open_contract": {
    "contract_id": 123456789,
    "is_sold": false,
    "profit": 0,
    "status": "open",
    "entry_tick": 1234.56,
    "current_tick": 1235.00,
    "sell_price": null
  }
}

// Quando finaliza:
{
  "proposal_open_contract": {
    "contract_id": 123456789,
    "is_sold": true,
    "profit": 9.85,
    "status": "won",
    "entry_tick": 1234.56,
    "exit_tick": 1240.00,
    "sell_price": 19.70
  }
}
```

### 3.2.8 Cancelar Assinatura
```json
{"forget": "subscription-uuid"}
```

---

## 3.3 Tipos de Contrato

### CALL / PUT (Opções Binárias)
```python
contract_types = {
    "CALL": "Win if exit > entry",
    "PUT":  "Win if exit < entry",
}
```

### Parâmetros
| Parâmetro | Valores | Descrição |
|-----------|---------|-----------|
| `contract_type` | `CALL`, `PUT` | Direção |
| `basis` | `stake`, `payout` | Base do valor |
| `amount` | float | Valor |
| `duration` | int | Número de unidades |
| `duration_unit` | `t` (ticks), `s` (seg), `m` (min), `h` (hora), `d` (dia) | Unidade |
| `symbol` | `R_100`, `R_75`, `R_50`, `R_25`, `R_10`, `1HZ` | Mercado |
| `currency` | `USD`, `EUR`, etc | Moeda |

---

## 3.4 Contratos Multiplicadores

O ZeeK também suporta modo **Multiplicador**:
```json
{
  "proposal": 1,
  "amount": 10,
  "basis": "stake",
  "contract_type": "MULTIPLIER",
  "currency": "USD",
  "symbol": "R_100",
  "duration": 3600,
  "duration_unit": "s",
  "multiplier": 10
}
```

---

## 3.5 Tratamento de Erros Comuns

| Código | Significado | Ação |
|--------|-------------|------|
| `InvalidToken` | Token inválido/expirado | Pedir novo token |
| `ProposalValidation` | Contrato inválido | Ajustar parâmetros |
| `ContractNotFound` | Contrato não encontrado | Aguardar |
| `BuyFailed` | Compra recusada | Verificar saldo |
| `RateLimit` | Muitas requisições | Aguardar |
| `Disconnect` | Conexão perdida | Reconectar com backoff |

---

## 3.6 Implementação no Backend

### Estrutura do `DerivClient`

```python
class DerivClient:
    """Gerencia a conexão WebSocket com a Deriv."""

    def __init__(self, app_id: int = 24332):
        self.app_id = app_id
        self.ws: WebSocket | None = None
        self.token: str | None = None
        self.authorized: bool = False
        self._subscriptions: dict = {}
        self._pending_requests: dict = {}
        self._request_id: int = 0

    async def connect(self):
        """Abre conexão WebSocket."""
        self.ws = await websockets.connect(
            f"wss://ws.derivws.com/websockets/v3?app_id={self.app_id}"
        )
        # Inicia task para ler mensagens
        asyncio.create_task(self._message_loop())

    async def authorize(self, token: str) -> dict:
        """Autentica na Deriv."""
        response = await self._send_and_wait({"authorize": token})
        self.token = token
        self.authorized = True
        return response

    async def subscribe_ticks(self, symbol: str) -> str:
        """Inscreve em ticks de um símbolo."""
        response = await self._send_and_wait({
            "subscribe": 1, "ticks": symbol
        })
        sub_id = response.get("subscription", {}).get("id")
        self._subscriptions[symbol] = sub_id
        return sub_id

    async def subscribe_balance(self):
        """Inscreve em atualizações de saldo."""
        return await self._send_and_wait({
            "subscribe": 1, "balance": 1
        })

    async def get_proposal(self, params: dict) -> dict:
        """Solicita cotação."""
        return await self._send_and_wait({
            "proposal": 1,
            **params
        })

    async def buy_contract(self, proposal_id: str, price: float) -> dict:
        """Compra um contrato."""
        return await self._send_and_wait({
            "buy": proposal_id,
            "price": price
        })

    async def _send_and_wait(self, msg: dict, timeout: float = 10) -> dict:
        """Envia mensagem e aguarda resposta."""
        req_id = self._next_id()
        msg["req_id"] = req_id
        future = asyncio.get_event_loop().create_future()
        self._pending_requests[req_id] = future
        await self.ws.send(json.dumps(msg))
        return await asyncio.wait_for(future, timeout)

    async def _message_loop(self):
        """Loop principal de recebimento."""
        async for message in self.ws:
            data = json.loads(message)
            # Verifica se é resposta a uma requisição
            req_id = data.get("req_id")
            if req_id and req_id in self._pending_requests:
                self._pending_requests[req_id].set_result(data)
                del self._pending_requests[req_id]
            # Notifica subscribers
            await self._notify_subscribers(data)

    async def _notify_subscribers(self, data: dict):
        """Distribui mensagem para subscribers registrados."""
        if "ticks" in data:
            await self._on_tick(data["ticks"])
        elif "balance" in data:
            await self._on_balance(data["balance"])
        elif "transaction" in data:
            await self._on_transaction(data["transaction"])
```

---

## 3.7 Considerações de Rate Limit

A Deriv tem limites de requisição. No ZeeK original:
- **Proposal:** Solicita-se proposal apenas quando a regra é ativada (não a cada tick)
- **Buy:** Executa imediatamente após proposal aceito
- **Ticks:** Stream passivo (assinatura única)
- **Reconexão:** Backoff exponencial (1s, 2s, 4s, 8s, max 60s)
