# Risk Management & Policy Engine

## Risk Framework Overview

### Capital Allocation Model
```python
class CapitalAllocation:
    """
    Kelly Criterion with safety adjustments
    """
    def calculate_position_size(self, signal):
        # Base Kelly
        win_prob = signal.confidence
        loss_prob = 1 - win_prob
        win_loss_ratio = signal.expected_rr
        
        kelly_fraction = (win_prob * win_loss_ratio - loss_prob) / win_loss_ratio
        
        # Safety adjustments
        kelly_fraction *= 0.25  # Use 1/4 Kelly
        
        # Mode-based caps
        max_size = {
            "demo": 0.10,
            "paper": 0.02,
            "live": 0.0025
        }[self.trading_mode]
        
        return min(kelly_fraction, max_size)
Risk Limits
Position-Level Limits
yamlsingle_position:
  max_size_percent: 0.25  # % of total capital
  max_loss_percent: 0.5   # % of total capital
  max_leverage: 3         # Maximum leverage multiplier
  min_rr_ratio: 1.5       # Minimum risk-reward ratio

correlation_limits:
  btc_eth_combined: 0.70  # Max combined exposure
  total_crypto: 1.00      # Max total exposure
  same_direction: 0.80    # Max same-direction exposure
Portfolio-Level Limits
yamlportfolio:
  max_open_positions: 5
  max_daily_trades: 10
  max_total_risk: 1.00    # % of capital at risk
  max_correlation_risk: 0.70
  
drawdown_limits:
  daily: 3.0             # % daily drawdown limit
  weekly: 7.0            # % weekly drawdown limit
  monthly: 15.0          # % monthly drawdown limit
  
  actions_on_breach:
    daily_3pct: "halt_new_trades"
    daily_5pct: "close_all_positions"
    weekly_7pct: "reduce_size_50pct"
    monthly_15pct: "switch_to_demo"
Dynamic Risk Adjustment
Volatility-Based Sizing
pythonclass VolatilityAdjustedSizing:
    def adjust_for_volatility(self, base_size, asset):
        # Get current vs historical volatility
        current_vol = self.get_current_volatility(asset)
        avg_vol = self.get_average_volatility(asset, days=30)
        
        vol_ratio = current_vol / avg_vol
        
        if vol_ratio > 2.0:  # High volatility
            return base_size * 0.5
        elif vol_ratio > 1.5:
            return base_size * 0.75
        elif vol_ratio < 0.5:  # Low volatility
            return base_size * 1.25
        else:
            return base_size
Regime-Based Adjustments
pythonMARKET_REGIMES = {
    "trending_bull": {
        "position_multiplier": 1.2,
        "stop_loss_multiplier": 0.8,
        "take_profit_multiplier": 1.5
    },
    "trending_bear": {
        "position_multiplier": 0.8,
        "stop_loss_multiplier": 1.2,
        "take_profit_multiplier": 0.8
    },
    "ranging": {
        "position_multiplier": 0.6,
        "stop_loss_multiplier": 1.0,
        "take_profit_multiplier": 1.0
    },
    "high_volatility": {
        "position_multiplier": 0.5,
        "stop_loss_multiplier": 1.5,
        "take_profit_multiplier": 1.2
    }
}
Stop Loss & Take Profit
ATR-Based Stop Loss
pythonclass StopLossCalculator:
    def calculate_stop(self, entry_price, side, asset):
        atr = self.get_atr(asset, period=14)
        
        # Base multiplier
        multiplier = 1.5
        
        # Adjust for volatility regime
        if self.market_regime == "high_volatility":
            multiplier = 2.0
        elif self.market_regime == "low_volatility":
            multiplier = 1.0
        
        stop_distance = atr * multiplier
        
        if side == "LONG":
            return entry_price - stop_distance
        else:
            return entry_price + stop_distance
Progressive Take Profit
pythonclass TakeProfitStrategy:
    def calculate_targets(self, entry_price, stop_loss, side):
        risk = abs(entry_price - stop_loss)
        
        targets = []
        levels = [
            {"rr": 1.0, "size_pct": 0.33},  # Take 1/3 at 1:1
            {"rr": 2.0, "size_pct": 0.33},  # Take 1/3 at 2:1
            {"rr": 3.0, "size_pct": 0.34}   # Take rest at 3:1
        ]
        
        for level in levels:
            if side == "LONG":
                price = entry_price + (risk * level["rr"])
            else:
                price = entry_price - (risk * level["rr"])
            
            targets.append({
                "price": price,
                "size_pct": level["size_pct"]
            })
        
        return targets
Policy Engine Rules
Pre-Trade Validation
pythonclass PolicyEngine:
    def validate_trade(self, proposed_trade):
        checks = {
            "risk_limit": self._check_risk_limit,
            "correlation": self._check_correlation,
            "drawdown": self._check_drawdown,
            "frequency": self._check_frequency,
            "time_restriction": self._check_time_restriction,
            "wallet_credibility": self._check_wallet_credibility
        }
        
        results = {}
        for check_name, check_func in checks.items():
            passed, reason = check_func(proposed_trade)
            results[check_name] = {"passed": passed, "reason": reason}
            
            if not passed and check_name in ["risk_limit", "drawdown"]:
                return False, results  # Hard rejection
        
        # Soft rejections (can be overridden)
        soft_failures = [k for k, v in results.items() 
                        if not v["passed"] and k not in ["risk_limit", "drawdown"]]
        
        if len(soft_failures) > 2:
            return False, results
        
        return True, results
Risk Monitoring
Real-time Risk Metrics
pythonclass RiskMonitor:
    def get_current_metrics(self):
        return {
            "open_positions": self.count_open_positions(),
            "total_exposure": self.calculate_total_exposure(),
            "current_drawdown": self.calculate_drawdown(),
            "risk_consumed": self.calculate_risk_consumed(),
            "correlation_risk": self.calculate_correlation_risk(),
            "var_95": self.calculate_var(confidence=0.95),
            "margin_usage": self.get_margin_usage(),
            "liquidation_distance": self.calculate_liquidation_distance()
        }
    
    def check_alerts(self, metrics):
        alerts = []
        
        if metrics["current_drawdown"] > 2.5:
            alerts.append(("WARNING", "Approaching daily drawdown limit"))
        
        if metrics["risk_consumed"] > 0.8:
            alerts.append(("WARNING", "High risk utilization"))
        
        if metrics["liquidation_distance"] < 0.1:
            alerts.append(("CRITICAL", "Close to liquidation"))
        
        return alerts
Emergency Procedures
Kill Switch
pythonclass KillSwitch:
    def __init__(self):
        self.triggers = {
            "manual": False,
            "drawdown": False,
            "technical": False,
            "regulatory": False
        }
    
    def activate(self, reason):
        self.triggers[reason] = True
        
        # Immediate actions
        self.cancel_all_pending_orders()
        self.close_all_positions_market()
        self.disable_new_trades()
        self.switch_to_safe_mode()
        
        # Notifications
        self.send_alerts(reason)
        self.log_activation(reason)
        
        return {
            "status": "activated",
            "reason": reason,
            "timestamp": datetime.now(),
            "positions_closed": self.closed_positions,
            "estimated_loss": self.calculate_emergency_loss()
        }
Recovery Procedures
pythonclass RecoveryManager:
    def post_incident_recovery(self, incident_type):
        steps = {
            "assess_damage": self.assess_damage(),
            "review_logs": self.review_audit_trail(),
            "identify_cause": self.root_cause_analysis(),
            "apply_fixes": self.apply_corrections(),
            "test_fixes": self.run_safety_tests(),
            "gradual_restart": self.gradual_reactivation()
        }
        
        for step_name, step_func in steps.items():
            result = step_func()
            if not result["success"]:
                return {"status": "failed", "failed_at": step_name}
        
        return {"status": "recovered", "steps": steps}
