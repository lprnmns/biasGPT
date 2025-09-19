# Trading Modes Configuration

## Overview
The system supports three trading modes with progressive safety features and automatic transitions based on performance metrics.

## Mode Definitions

### 1. Demo Mode
- **Purpose**: System testing and development
- **Characteristics**:
  - Uses OKX demo environment
  - Fake balance ($10,000 default)
  - No real money at risk
  - All features enabled for testing
  - No rate limits on LLM calls

**OKX Configuration**:
```javascript{
baseURL: "https://www.okx.com/api/v5",
wsURL: "wss://wspap.okx.com:8443/ws/v5/public",
headers: {
"x-simulated-trading": "1"
}
}

### 2. Paper Trading Mode
- **Purpose**: Strategy validation with real market data
- **Characteristics**:
  - Real market data
  - Simulated order execution
  - Realistic slippage modeling (0.05% default)
  - Real-time P&L tracking
  - Performance metrics collection

**Transition Criteria to Live**:
- Minimum 14 days in paper mode
- Sharpe ratio > 1.5
- Max drawdown < 5%
- Win rate > 55%
- Manual approval required

### 3. Live Trading Mode
- **Purpose**: Real money trading
- **Characteristics**:
  - Real order execution
  - Progressive capital allocation
  - Strict risk limits enforced
  - Full audit logging
  - Automatic protection mechanisms

**Safety Features**:
- Start with 1% capital allocation
- Gradual increase based on performance
- Maximum 10% total allocation
- Automatic reversion to paper on breach

## Environment Variables

### Demo Mode
```bashOKX_MODE=demo
OKX_API_KEY=your_demo_key
OKX_API_SECRET=your_demo_secret
OKX_API_PASSPHRASE=your_demo_passphrase
OKX_SIMULATED_TRADING=1
RISK_MULTIPLIER=1.0
LLM_RATE_LIMIT=100

### Paper Trading Mode
```bashOKX_MODE=paper
OKX_API_KEY=your_paper_key
OKX_API_SECRET=your_paper_secret
OKX_API_PASSPHRASE=your_paper_passphrase
OKX_SIMULATED_TRADING=1
RISK_MULTIPLIER=0.5
LLM_RATE_LIMIT=50

### Live Trading Mode
```bashOKX_MODE=live
OKX_API_KEY=your_live_key
OKX_API_SECRET=your_live_secret
OKX_API_PASSPHRASE=your_live_passphrase
OKX_SIMULATED_TRADING=0
RISK_MULTIPLIER=0.25
LLM_RATE_LIMIT=20
REQUIRES_2FA=true

## Mode Transition Logic

### Automatic Transitions
```pythonclass TradingModeManager:
def check_mode_transition(self):
if self.mode == "demo":
if self.days_active >= 7 and self.backtest_sharpe > 1.0:
self.request_transition("paper")    elif self.mode == "paper":
        if self.meets_live_criteria() and self.has_manual_approval():
            self.transition_to("live", capital_pct=0.01)    elif self.mode == "live":
        if self.daily_drawdown > 0.05:
            self.emergency_transition("paper")
            self.send_alert("Reverted to paper trading due to drawdown")

### Manual Controls
- Users can always manually switch to a safer mode
- Switching to a riskier mode requires:
  - 2FA confirmation
  - Email verification
  - 24-hour cooldown period

## Risk Scaling by Mode

| Metric | Demo | Paper | Live (Start) | Live (Full) |
|--------|------|-------|--------------|-------------|
| Max Position Size | 10% | 2% | 0.25% | 1% |
| Max Daily Loss | 20% | 5% | 1% | 3% |
| Max Leverage | 10x | 5x | 2x | 3x |
| Stop Loss Buffer | 1x ATR | 1.5x ATR | 2x ATR | 1.5x ATR |
| LLM Calls/Hour | 100 | 50 | 20 | 20 |

## Monitoring & Alerts

### Mode-Specific Metrics
```yamldemo:
track:
- system_errors
- api_latency
- event_processing_ratepaper:
track:
- simulated_pnl
- sharpe_ratio
- max_drawdown
- win_rate
alert_on:
- sharpe < 1.0
- drawdown > 7%live:
track:
- real_pnl
- risk_utilization
- order_slippage
- funding_costs
alert_on:
- drawdown > 3%
- risk_utilization > 80%
- unusual_slippage > 0.1%

## Testing Requirements by Mode

### Before Demo → Paper
- [ ] All unit tests passing
- [ ] Integration tests passing  
- [ ] 1000 historical events processed successfully
- [ ] Kill switch tested

### Before Paper → Live
- [ ] 14 days of paper trading data
- [ ] Backtesting on 6 months of data
- [ ] Risk model validation
- [ ] Disaster recovery tested
- [ ] Security audit completed
