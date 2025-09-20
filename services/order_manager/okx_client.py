"""OKX demo client focusing on request signing."""

from __future__ import annotations

import base64
import hashlib
import hmac
import json
import time
from dataclasses import dataclass
from typing import Any, Dict, Optional, Protocol


DEFAULT_BASE_URL = "https://www.okx.com"


@dataclass(slots=True)
class OKXCredentials:
    api_key: str
    secret_key: str
    passphrase: str


class Transport(Protocol):
    async def post(self, path: str, headers: Dict[str, str], body: str) -> Dict[str, Any]:  # pragma: no cover - interface
        ...


class MemoryTransport:
    """Testing transport that records requests."""

    def __init__(self, response: Optional[Dict[str, Any]] = None) -> None:
        self.response = response or {"state": "ok"}
        self.last_call: Optional[Dict[str, Any]] = None

    async def post(self, path: str, headers: Dict[str, str], body: str) -> Dict[str, Any]:
        self.last_call = {"path": path, "headers": headers, "body": body}
        return self.response


class OKXClient:
    def __init__(
        self,
        credentials: OKXCredentials,
        *,
        base_url: str = DEFAULT_BASE_URL,
        simulated: bool = True,
        transport: Optional[Transport] = None,
    ) -> None:
        self.credentials = credentials
        self.base_url = base_url.rstrip("/")
        self.simulated = simulated
        self.transport = transport or MemoryTransport()

    async def create_order(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        return await self._post("/api/v5/trade/order", payload)

    async def _post(self, path: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        body = json.dumps(payload, separators=(",", ":"))
        timestamp = self._timestamp()
        signature = self._sign(timestamp, "POST", path, body)
        headers = {
            "OK-ACCESS-KEY": self.credentials.api_key,
            "OK-ACCESS-PASSPHRASE": self.credentials.passphrase,
            "OK-ACCESS-SIGN": signature,
            "OK-ACCESS-TIMESTAMP": timestamp,
        }
        if self.simulated:
            headers["x-simulated-trading"] = "1"
        return await self.transport.post(path, headers, body)

    def _sign(self, timestamp: str, method: str, path: str, body: str) -> str:
        message = f"{timestamp}{method.upper()}{path}{body}".encode()
        secret = self.credentials.secret_key.encode()
        hash_digest = hmac.new(secret, message, hashlib.sha256).digest()
        return base64.b64encode(hash_digest).decode()

    def _timestamp(self) -> str:
        return f"{time.time():.0f}"


__all__ = ["OKXClient", "OKXCredentials", "MemoryTransport"]
