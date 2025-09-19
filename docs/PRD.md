# Product Requirements Document (PRD) — Whale-Driven AI Trader

## 0. Executive Summary
Automated trading system that monitors 10-15 whale wallets on Ethereum, analyzes their behavior using LLM (Groq Llama-4), and executes leveraged trades on OKX based on calculated bias. Features progressive deployment from demo → paper → live trading.

## 1. Core Objectives
### Primary Goals
- **H1: Real-time Monitoring** — Track 10-15 whale addresses with <2s latency via Alchemy WebSocket
- **H2: Intelligent Scoring** — Dynamic wallet credibility (0-10) and directional bias using EWMA + LLM analysis
- **H3: Automated Execution** — Risk-controlled order placement on OKX (demo → paper → live progression)
- **H4: Reporting System** — 4-hourly automated reports with push notifications and chat explanations
- **H5: Security First** — Zero withdrawal permissions, API key rotation, comprehensive audit logging

### Success Metrics
- 7-day hit rate > 55%
- Sharpe ratio > 1.5 (paper trading)
- System uptime ≥ 99.5%
- Max drawdown < 10%
- LLM cost < $10/day

## 2. Scope
### Included (MVP)
- Ethereum mainnet wallet monitoring (Alchemy + Etherscan)
- Event classification: deposit_cex, withdraw_cex, swap, transfer, bridge
- Multi-timeframe scoring (1h, 4h, 24h) with credibility weighting
- LLM integration for high-impact events only (cost optimization)
- Progressive OKX integration: demo → paper → live
- Next.js PWA with chat interface and push notifications
- Kill-switch mechanism (manual + automatic triggers)
- Basic backtesting framework

### Excluded (Post-MVP)
- Multi-chain support (BSC, Arbitrum, Polygon)
- Advanced ML models (transformers, LSTM)
- Social sentiment analysis
- MEV detection
- Copy trading for other users

## 3. User Journey
1. **Setup**: User logs in → Adds whale addresses → System fetches history
2. **Monitoring**: Real-time event detection → Score updates → Bias calculation
3. **Decision**: LLM analysis (if triggered) → Policy validation → Risk checks
4. **Execution**: Order placement → Position monitoring → Auto stop-loss/take-profit
5. **Reporting**: 4h summary → Push notification → Chat explanation available

## 4. Trading Progression Strategy
### Phase 1: Demo Mode (Weeks 1-2)
- Full system testing with simulated trades
- No real money at risk
- Metric collection and baseline establishment

### Phase 2: Paper Trading (Weeks 3-4)
- Real market data, simulated execution
- Performance validation against backtest
- Risk model calibration

### Phase 3: Canary Live (Week 5)
- 1% of capital allocation
- Strict risk limits (0.25% per trade max)
- Manual approval required for trades > $100

### Phase 4: Production (Week 6+)
- Gradual capital increase based on performance
- Max 10% total capital allocation
- Automated risk scaling

## 5. Risk Management Framework
### Position Limits
- Single trade risk: ≤ 0.25% of capital
- Total portfolio risk: ≤ 1.0%
- Correlation cluster limit: ≤ 0.7% (BTC+ETH+L1s)
- Max leverage: 3x (configurable by environment)

### Circuit Breakers
- Daily drawdown > 3%: halt trading
- Weekly drawdown > 7%: reduce size by 50%
- Monthly drawdown > 15%: revert to demo mode
- LLM errors > 10%: fallback to rule-based

## 6. Technical Constraints
- Zero-cost infrastructure target (free tiers only for MVP)
- LLM calls limited to 20/hour to control costs
- Maximum 100 events/second processing capability
- 5GB database storage limit (Neon free tier)

## 7. Compliance & Legal
- "Not financial advice" disclaimer required
- User must accept full risk responsibility
- No US users without KYC (Phase 2)
- Audit trail for all trading decisions
