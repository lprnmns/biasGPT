# API
# API Documentation

## Authentication
All endpoints except `/health` and `/v1/auth/*` require JWT authentication.

### HeadersAuthorization: Bearer <jwt_token>
X-Request-ID: <uuid>
Content-Type: application/json

## Response Format
### Success
```json{
"success": true,
"data": { ... },
"meta": {
"timestamp": "2025-01-01T00:00:00Z",
"request_id": "uuid",
"version": "1.0.0"
}
}

### Error
```json{
"success": false,
"error": {
"code": "ERROR_CODE",
"message": "Human readable message",
"details": { ... }
},
"meta": { ... }
}

## Endpoints

### Public Endpoints

#### POST /v1/auth/register
```jsonRequest:
{
"email": "user@example.com",
"password": "hashed_password",
"agreed_terms": true
}Response:
{
"user_id": "usr_xxx",
"email": "user@example.com",
"verification_required": true
}

#### POST /v1/auth/login
```jsonRequest:
{
"email": "user@example.com",
"password": "hashed_password",
"otp": "123456"  // optional, for 2FA
}Response:
{
"access_token": "jwt...",
"refresh_token": "jwt...",
"expires_in": 3600,
"user": {
"id": "usr_xxx",
"email": "user@example.com",
"trading_mode": "demo"
}
}

### Protected Endpoints

#### GET /v1/dashboard
Returns dashboard data including positions, P&L, and recent events.

#### POST /v1/wallets
Add wallet to watchlist
```jsonRequest:
{
"address": "0x...",
"label": "Smart Money #1",
"initial_credibility": 5.0
}

#### GET /v1/wallets
Get all watched wallets with current scores

#### GET /v1/bias
Get current bias vector for all assets

#### GET /v1/positions
Get open positions with real-time P&L

#### POST /v1/chat
Chat with AI assistant
```jsonRequest:
{
"message": "Why did we open that BTC position?",
"context_window": 10
}Response:
{
"reply": "The position was opened because...",
"citations": ["evt_123", "evt_456"],
"confidence": 0.85
}

### Internal Service Endpoints

#### POST /internal/events/ingest
```jsonRequest:
{
"events": [
{
"wallet": "0x...",
"type": "transfer",
"asset": "ETH",
"amount": 100.5,
"to": "0x...",
"tx_hash": "0x...",
"timestamp": "2025-01-01T00:00:00Z"
}
]
}

#### POST /internal/llm/analyze
```jsonRequest:
{
"event": { ... },
"context": {
"wallet_credibility": 7.5,
"recent_events": [ ... ]
}
}Response:
{
"classification": "whale_accumulation",
"confidence": 0.85,
"proposed_action": {
"type": "LONG",
"asset": "ETH",
"size_pct": 0.25
},
"reasoning": "Based on..."
}

#### POST /internal/orders/execute
```jsonRequest:
{
"mode": "demo|paper|live",
"order": {
"asset": "ETHUSDT",
"side": "BUY",
"type": "MARKET",
"size": 0.1,
"stop_loss": 3400,
"take_profit": [3600, 3700]
}
}

## Rate Limits
- Public endpoints: 10 req/min
- Protected endpoints: 60 req/min  
- Chat endpoint: 20 req/hour
- Internal endpoints: No limit

## Error Codes
- `AUTH_INVALID`: Invalid credentials
- `AUTH_EXPIRED`: Token expired
- `RATE_LIMITED`: Too many requests
- `WALLET_EXISTS`: Wallet already in watchlist
- `INSUFFICIENT_BALANCE`: Not enough balance for trade
- `RISK_EXCEEDED`: Risk limits exceeded
- `LLM_ERROR`: LLM service error
- `EXCHANGE_ERROR`: OKX API error
