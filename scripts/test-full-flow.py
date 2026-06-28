#!/usr/bin/env python3
"""Test full connection flow: login, WS connect, authorize Deriv."""
import asyncio
import json
import sys
import httpx
import websockets

BACKEND = "http://localhost:8001"
WS_URL = "ws://localhost:8001/api/ws/"
PAT_TOKEN = "BPaQmx5K5qOvuDE"


async def main():
    # 1. Login
    print("1. Logging in...")
    async with httpx.AsyncClient() as client:
        r = await client.post(
            f"{BACKEND}/api/auth/register?email=bot@test.com&password=admin123"
        )
        if r.status_code == 400:
            r = await client.post(
                f"{BACKEND}/api/auth/login?email=bot@test.com&password=admin123"
            )
        data = r.json()
        jwt = data["access_token"]
        print(f"   JWT: {jwt[:30]}...")

    # 2. Connect via WS
    print(f"2. Connecting WS...")
    ws_url = f"{WS_URL}?token={jwt}"

    try:
        async with websockets.connect(ws_url) as ws:
            print("   WS connected!")

            # Receive initial status
            resp = await asyncio.wait_for(ws.recv(), timeout=5)
            print(f"   Initial: {resp[:80]}")

            # Send connect_deriv
            msg = json.dumps({"action": "connect_deriv", "pat_token": PAT_TOKEN})
            print(f"   Sending connect_deriv...")
            await ws.send(msg)

            # Listen for responses for up to 30 seconds
            print("   Listening for connection result...")
            connected = False
            for i in range(60):
                try:
                    resp = await asyncio.wait_for(ws.recv(), timeout=0.5)
                    data = json.loads(resp)
                    msg_type = data.get("type", "?")

                    if msg_type in ("deriv_status", "status"):
                        if data.get("connected"):
                            connected = True
                            balance = data.get("balance", {})
                            print(
                                f"\n   ✅ DERIV CONNECTED! "
                                f"Balance: {balance.get('balance')} {balance.get('currency')}"
                            )
                            break
                    elif msg_type == "error":
                        print(f"\n   ❌ ERROR: {data.get('message')}")
                        break
                    elif msg_type == "deriv_connecting":
                        if i % 5 == 0:
                            print(f"   ⏳ Connecting...")
                except asyncio.TimeoutError:
                    if i > 0 and i % 10 == 0:
                        print(f"   ⏳ Still waiting... ({i}s)")

            if connected:
                print("\n3. ✅ Deriv connected successfully!")
            else:
                print("\n3. ❌ Failed to connect (timeout)")

    except Exception as e:
        print(f"   Error: {e}")
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))
