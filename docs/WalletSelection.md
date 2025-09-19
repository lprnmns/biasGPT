# Whale Wallet Selection & Scoring

## Initial Wallet Discovery

### Data Sources
1. **Etherscan**: Top holders by token
2. **Nansen**: Smart money labels
3. **Arkham**: Entity identification
4. **DeFiLlama**: Protocol treasuries
5. **Manual**: Known fund addresses

### Selection Criteria
```pythonclass WalletSelectionCriteria:
MIN_BALANCE_USD = 1_000_000
MIN_TX_COUNT_30D = 10
MIN_LIFETIME_VOLUME_USD = 10_000_000
MAX_FAILED_TX_RATIO = 0.1EXCLUDE_PATTERNS = [
    "exchange_hot_wallet",
    "bridge_contract",
    "mev_bot",
    "airdrop_distributor"
]PRIORITY_LABELS = [
    "smart_money",
    "fund",
    "whale",
    "insider"
]

## Wallet Scoring Framework

### Multi-Factor Scoring Model
```pythonclass WalletScorer:
def calculate_credibility(self, wallet_address):
scores = {
"historical_performance": self._score_historical(),
"trading_sophistication": self._score_sophistication(),
"consistency": self._score_consistency(),
"timing_quality": self._score_timing(),
"risk_management": self._score_risk_mgmt()
}    weights = {
        "historical_performance": 0.35,
        "trading_sophistication": 0.25,
        "consistency": 0.15,
        "timing_quality": 0.15,
        "risk_management": 0.10
    }    return sum(scores[k] * weights[k] for k in scores)def _score_historical(self):
    """
    Based on past trade outcomes
    """
    trades = self.get_closed_trades()
    win_rate = len([t for t in trades if t.pnl > 0]) / len(trades)
    avg_winner = np.mean([t.pnl for t in trades if t.pnl > 0])
    avg_loser = abs(np.mean([t.pnl for t in trades if t.pnl < 0]))    # Expectancy calculation
    expectancy = (win_rate * avg_winner) - ((1 - win_rate) * avg_loser)    return min(10, expectancy * 2)  # Scale to 0-10

### Dynamic Credibility Updates
```pythonclass CredibilityUpdater:
def update_after_trade(self, wallet, predicted_outcome, actual_outcome):
"""
Bayesian update of wallet credibility
"""
accuracy = 1 - abs(predicted_outcome - actual_outcome)    # EWMA update
    alpha = 0.1  # Learning rate
    wallet.credibility = (alpha * accuracy * 10) + ((1 - alpha) * wallet.credibility)    # Confidence bounds
    wallet.confidence_lower = wallet.credibility - (1.96 * wallet.std_dev)
    wallet.confidence_upper = wallet.credibility + (1.96 * wallet.std_dev)

## Wallet Behavior Classification

### Behavioral Patterns
```pythonWALLET_ARCHETYPES = {
"accumulator": {
"indicators": ["consistent_buying", "low_sell_ratio", "long_hold_time"],
"weight": 1.2,
"preferred_timeframe": "4h"
},
"swing_trader": {
"indicators": ["regular_trades", "profit_taking", "stop_losses"],
"weight": 1.0,
"preferred_timeframe": "1h"
},
"dumper": {
"indicators": ["large_sells", "cex_deposits", "token_liquidation"],
"weight": 0.8,
"preferred_timeframe": "15m"
},
"market_maker": {
"indicators": ["high_volume", "narrow_spreads", "balanced_flow"],
"weight": 0.5,
"preferred_timeframe": "1h"
}
}

## Watchlist Management

### Auto-Discovery Pipeline
```pythonclass WalletDiscovery:
async def discover_new_whales(self):
candidates = []    # Check interaction partners of existing whales
    for whale in self.active_whales:
        partners = await self.get_transaction_partners(whale)
        candidates.extend(partners)    # Filter and score
    qualified = []
    for candidate in candidates:
        if self.meets_criteria(candidate):
            score = self.initial_score(candidate)
            qualified.append((candidate, score))    # Add top candidates
    qualified.sort(key=lambda x: x[1], reverse=True)
    return qualified[:5]

### Pruning Underperformers
```pythonclass WalletPruner:
def evaluate_for_removal(self):
remove_list = []    for wallet in self.watchlist:
        # Check recent performance
        if wallet.credibility < 3.0:
            if wallet.days_watched > 30:
                remove_list.append(wallet)        # Check activity
        if wallet.last_transaction_days > 14:
            remove_list.append(wallet)        # Check signal quality
        if wallet.false_signal_rate > 0.5:
            remove_list.append(wallet)    return remove_list

## Performance Tracking

### Wallet Metrics Dashboard
```sqlCREATE VIEW wallet_performance AS
SELECT
w.address,
w.label,
w.credibility,
COUNT(DISTINCT e.id) as total_events_30d,
SUM(CASE WHEN t.pnl > 0 THEN 1 ELSE 0 END)::FLOAT /
NULLIF(COUNT(t.id), 0) as win_rate,
AVG(t.pnl) as avg_trade_pnl,
MAX(t.pnl) as best_trade,
MIN(t.pnl) as worst_trade,
STDDEV(t.pnl) as pnl_volatility
FROM wallets w
LEFT JOIN events e ON w.id = e.wallet_id
AND e.timestamp > NOW() - INTERVAL '30 days'
LEFT JOIN trades t ON t.signal_wallet_id = w.id
AND t.closed_at IS NOT NULL
GROUP BY w.address, w.label, w.credibility
ORDER BY w.credibility DESC;

## Special Considerations

### MEV and Sandwich Detection
```pythondef is_mev_activity(transaction):
"""
Detect and filter MEV/sandwich attacks
"""
indicators = {
"same_block_trades": check_same_block(),
"minimal_profit": transaction.profit_usd < 100,
"high_gas": transaction.gas_price > avg_gas * 3,
"known_mev_contract": transaction.to in MEV_CONTRACTS
}return sum(indicators.values()) >= 2

### Exchange Hot Wallet Filtering
```pythonEXCHANGE_PATTERNS = {
"high_tx_frequency": lambda w: w.daily_tx_count > 1000,
"round_numbers": lambda w: w.common_amounts_ratio > 0.5,
"diverse_tokens": lambda w: w.unique_token_count > 100,
"labeled_cex": lambda w: w.etherscan_label in CEX_LABELS
}
