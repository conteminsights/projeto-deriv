#!/usr/bin/env python3
"""Test a Deriv PAT token directly against the API."""
import asyncio
import json
import websockets

async def test_token(token: str):
    token = token.strip()
    print(f"Testing token: '{token}' ({len(token)} chars)")
    print(f"All alphanumeric: {token.isalnum()}")
    
    url = "wss://ws.derivws.com/websockets/v3?app_id=1089"
    
    try:
        async with websockets.connect(url) as ws:
            print("Connected to Deriv WS")
            
            # Send authorize
            msg = json.dumps({"authorize": token, "req_id": 1})
            print(f"Sending: {{\"authorize\": \"{token[:4]}...\", \"req_id\": 1}}")
            await ws.send(msg)
            
            # Wait for response
            response = await asyncio.wait_for(ws.recv(), timeout=10)
            data = json.loads(response)
            
            if "error" in data:
                print(f"ERROR: {data['error']}")
                if "InputValidationFailed" in str(data):
                    print("→ Token format is INVALID")
                elif "InvalidToken" in str(data):
                    print("→ Token is REVOKED or WRONG")
            else:
                auth = data.get("authorize", {})
                loginid = auth.get("loginid", "?")
                balance = auth.get("balance", "?")
                currency = auth.get("currency", "?")
                accounts = auth.get("account_list", [])
                print(f"SUCCESS! LoginID: {loginid}, Balance: {balance} {currency}")
                print(f"Accounts ({len(accounts)}):")
                for acc in accounts:
                    virt = "(Demo)" if acc.get("is_virtual") else "(Real)"
                    print(f"  {acc['loginid']} {acc['currency']} {virt}")
    
    except asyncio.TimeoutError:
        print("TIMEOUT - no response from server")
    except websockets.WebSocketException as e:
        print(f"WebSocket error: {e}")
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    import sys
    token = sys.argv[1] if len(sys.argv) > 1 else ""
    if not token:
        print("Usage: python3 test-token.py <PAT_TOKEN>")
        sys.exit(1)
    asyncio.run(test_token(token))
