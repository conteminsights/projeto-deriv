#!/usr/bin/env python3
"""Connect Deriv, create strategy, start operating.
Usage: python3 setup-and-run.py <PAT_TOKEN>"""
import asyncio
import json
import httpx
import websockets
import sys

BACKEND = "http://127.0.0.1:8000"
WS_URL = "ws://127.0.0.1:8000/api/ws/"


async def main():
    if len(sys.argv) < 2:
        print("Usage: setup-and-run.py <PAT_TOKEN>")
        return 1

    pat_token = sys.argv[1].strip()
    print("=== SETUP: Contem Insights Trade ===")

    # 1. Login
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BACKEND}/api/auth/register?email=operator@trade.com&password=trade123"
        )
        if r.status_code in (200, 201):
            jwt = r.json()["access_token"]
        else:
            r = await c.post(
                f"{BACKEND}/api/auth/login?email=operator@trade.com&password=trade123"
            )
            jwt = r.json()["access_token"]
    print(f"[1/5] Logged in")

    # 2. Connect WS, send connect_deriv, wait
    print(f"[2/5] Connecting WS & sending PAT...")
    ws = await websockets.connect(f"{WS_URL}?token={jwt}")
    await ws.send(
        json.dumps({"action": "connect_deriv", "pat_token": pat_token})
    )

    deriv_ok = False
    for i in range(50):
        try:
            resp = await asyncio.wait_for(ws.recv(), timeout=0.5)
            d = json.loads(resp)
            t = d.get("type", "")
            if t == "status" and d.get("connected"):
                deriv_ok = True
                bal = d.get("balance", {})
                print(f"      ✅ Deriv connected! Balance: {bal}")
                break
            elif t == "error":
                print(f"      ❌ Error: {d.get('message')}")
                break
        except asyncio.TimeoutError:
            if i % 10 == 0:
                print(f"      ⏳ Waiting... ({i//2}s)")

    if not deriv_ok:
        print("      ⚠️  Deriv not connected (timeout)")
        async with httpx.AsyncClient() as c:
            r = await c.get(f"{BACKEND}/api/status/")
            print(f"      Status: {r.json()}")
    await ws.close()

    # 3. Create DIGITODD strategy
    print(f"[3/5] Creating DIGITODD strategy...")
    strategy = {
        "name": "Auto Odd R100",
        "description": "DIGITODD every tick, mini-meta $20",
        "pages": [
            {
                "name": "Pagina 1",
                "market": "R_100",
                "mode": "CALL_PUT",
                "rules": [
                    {
                        "condition": {
                            "indicator": "price",
                            "operator": ">",
                            "value": 0,
                            "timeframe": 14,
                        },
                        "contract_type": "DIGITODD",
                        "duration": 1,
                        "duration_unit": "t",
                    }
                ],
            }
        ],
        "management": {
            "initial_stake": 2.0,
            "mini_meta_enabled": True,
            "mini_meta_target": 20.0,
            "auto_reload_enabled": True,
            "auto_reload_minutes": 60,
            "limits_enabled": True,
            "daily_loss_limit": 50.0,
            "session_loss_limit": 20.0,
            "consecutive_loss_limit": 5,
        },
    }
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BACKEND}/api/strategies/",
            json=strategy,
            headers={"Authorization": f"Bearer {jwt}"},
        )
        sid = r.json().get("id")
        print(f"      Strategy #{sid} created")

    # 4. Activate
    print(f"[4/5] Activating strategy...")
    async with httpx.AsyncClient() as c:
        r = await c.post(
            f"{BACKEND}/api/strategies/{sid}/activate",
            headers={"Authorization": f"Bearer {jwt}"},
        )
        print(f"      {r.json().get('message')}")

    print()
    print("=" * 50)
    if deriv_ok:
        print("✅ ALL SET! System running:")
    else:
        print("⚠️  Strategy active. Connect Deriv manually in Config page.")
        print("   Token might need re-entry in the browser.")
    print("   Strategy: Auto Odd R100 (DIGITODD)")
    print("   Stake: $2.00, Mini-meta: $20")
    print("=" * 50)
    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
