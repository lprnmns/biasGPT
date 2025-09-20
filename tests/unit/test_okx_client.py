import base64
import hashlib
import hmac

import pytest

from services.order_manager.okx_client import MemoryTransport, OKXClient, OKXCredentials


@pytest.mark.asyncio
async def test_okx_signature(monkeypatch):
    creds = OKXCredentials(api_key="key", secret_key="secret", passphrase="pass")
    client = OKXClient(creds)
    monkeypatch.setattr(client, "_timestamp", lambda: "1700000000")
    signature = client._sign("1700000000", "POST", "/api/v5/test", "{}")
    expected = base64.b64encode(hmac.new(b"secret", b"1700000000POST/api/v5/test{}", hashlib.sha256).digest()).decode()
    assert signature == expected


@pytest.mark.asyncio
async def test_create_order_records_request(monkeypatch):
    transport = MemoryTransport(response={"state": "simulated"})
    creds = OKXCredentials(api_key="key", secret_key="secret", passphrase="pass")
    client = OKXClient(creds, transport=transport)
    monkeypatch.setattr(client, "_timestamp", lambda: "1700000000")

    payload = {"instId": "BTC-USDT-SWAP", "tdMode": "cross"}
    result = await client.create_order(payload)

    assert result == {"state": "simulated"}
    assert transport.last_call is not None
    assert transport.last_call["path"] == "/api/v5/trade/order"
    headers = transport.last_call["headers"]
    assert headers["OK-ACCESS-KEY"] == "key"
    assert headers["x-simulated-trading"] == "1"
