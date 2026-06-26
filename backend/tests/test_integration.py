"""
ZeeK.Web — Integration tests: health, auth, tokens, strategies, bankroll
"""
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_health(client: AsyncClient):
    """Health endpoint should return OK."""
    resp = await client.get("/health")
    assert resp.status_code == 200
    data = resp.json()
    assert data["status"] == "ok"
    assert data["version"] == "1.0.0"


@pytest.mark.asyncio
async def test_register_and_login(client: AsyncClient):
    """Should register a user and login with JWT."""
    # Register
    resp = await client.post("/api/auth/register", params={"email": "test@test.com", "password": "test123"})
    assert resp.status_code == 200, f"Register failed: {resp.text}"
    data = resp.json()
    assert "access_token" in data
    assert data["email"] == "test@test.com"
    token = data["access_token"]

    # Login
    resp = await client.post("/api/auth/login", params={"email": "test@test.com", "password": "test123"})
    assert resp.status_code == 200
    assert resp.json()["access_token"] == token  # Same user, same token

    # Wrong password
    resp = await client.post("/api/auth/login", params={"email": "test@test.com", "password": "wrong"})
    assert resp.status_code == 401


@pytest.mark.asyncio
async def test_tokens_crud(client: AsyncClient):
    """Should create, list, and delete PAT tokens."""
    # Register first
    resp = await client.post("/api/auth/register", params={"email": "token@test.com", "password": "test123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}"}

    # Create token
    resp = await client.post("/api/tokens/",
        params={"token_value": "fake_pat_123", "label": "demo"},
        headers=headers)
    assert resp.status_code == 200
    assert resp.json()["label"] == "demo"

    # List tokens
    resp = await client.get("/api/tokens/", headers=headers)
    assert resp.status_code == 200
    tokens_list = resp.json()
    assert len(tokens_list) == 1
    assert tokens_list[0]["label"] == "demo"

    # Delete token
    resp = await client.delete("/api/tokens/1", headers=headers)
    assert resp.status_code == 200

    # List should be empty
    resp = await client.get("/api/tokens/", headers=headers)
    assert len(resp.json()) == 0


@pytest.mark.asyncio
async def test_strategies_crud(client: AsyncClient):
    """Should create, list, get, update, and delete strategies."""
    resp = await client.post("/api/auth/register", params={"email": "strat@test.com", "password": "test123"})
    token = resp.json()["access_token"]
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}

    # Create
    payload = {
        "name": "SMA Cross",
        "description": "Test strategy",
        "pages": [{"name": "P1", "market": "R_100", "mode": "CALL_PUT", "rules": []}],
        "management": {"initial_stake": 2.0},
    }
    resp = await client.post("/api/strategies/", json=payload, headers=headers)
    assert resp.status_code == 200, f"Create failed: {resp.text}"
    strat_id = resp.json()["id"]

    # List
    resp = await client.get("/api/strategies/", headers=headers)
    assert len(resp.json()) == 1

    # Get
    resp = await client.get(f"/api/strategies/{strat_id}", headers=headers)
    assert resp.json()["name"] == "SMA Cross"

    # Update
    resp = await client.put(f"/api/strategies/{strat_id}",
        json={"name": "SMA Cross v2"}, headers=headers)
    assert resp.json()["name"] == "SMA Cross v2"

    # Delete
    resp = await client.delete(f"/api/strategies/{strat_id}", headers=headers)
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_bankroll_endpoints(client: AsyncClient):
    """Bankroll config, defense, and reset should work."""
    # Get bankroll
    resp = await client.get("/api/bankroll/")
    assert resp.status_code == 200
    data = resp.json()
    assert "config" in data
    assert "state" in data
    assert data["config"]["initial_stake"] == 2.0

    # Update bankroll
    resp = await client.put("/api/bankroll/config",
        json={"initial_stake": 5.0, "martingale": {"enabled": True, "multiplier": 2.0, "max_steps": 3}})
    assert resp.status_code == 200
    assert resp.json()["config"]["initial_stake"] == 5.0

    # Defense get
    resp = await client.get("/api/bankroll/defense/page_1")
    assert resp.status_code == 200
    assert resp.json()["mode"] == "none"

    # Defense update
    resp = await client.put("/api/bankroll/defense/page_1",
        json={"mode": "barrier", "barrier": 3})
    assert resp.status_code == 200
    assert resp.json()["mode"] == "barrier"

    # Reset
    resp = await client.post("/api/bankroll/reset")
    assert resp.status_code == 200


@pytest.mark.asyncio
async def test_status_endpoint(client: AsyncClient):
    """Status endpoint should return server info."""
    resp = await client.get("/api/status/")
    assert resp.status_code == 200
    data = resp.json()
    assert data["server"] == "ok"
    assert data["version"] == "1.0.0"
    assert "deriv_connected" in data
