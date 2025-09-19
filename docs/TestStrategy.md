# Comprehensive Testing Strategy

## Testing Pyramid

### Level 1: Unit Tests (60%)
Fast, isolated tests for individual functions
```python
# tests/unit/test_scoring.py
import pytest
from services.scoring import WalletScorer

class TestWalletScoring:
    def test_credibility_calculation(self):
        scorer = WalletScorer()
        result = scorer.calculate_credibility({
            "win_rate": 0.6,
            "avg_pnl": 1000,
            "consistency": 0.8
        })
        assert 5.0 <= result <= 7.0
    
    def test_ewma_update(self):
        old_score = 5.0
        new_observation = 8.0
        alpha = 0.1
        expected = (alpha * new_observation) + ((1 - alpha) * old_score)
        
        result = scorer.update_ewma(old_score, new_observation, alpha)
        assert abs(result - expected) < 0.001
    
    @pytest.mark.parametrize("size_frac,expected", [
        (0.05, False),  # Too small
        (0.15, True),   # Valid
        (0.80, True),   # Large, valid
    ])
    def test_should_trigger_llm(self, size_frac, expected):
        assert trigger_decision(size_frac) == expected
Level 2: Integration Tests (30%)
Test component interactions
python# tests/integration/test_trading_flow.py
class TestTradingFlow:
    @pytest.mark.asyncio
    async def test_event_to_trade_flow(self, db_session):
        # Create test event
        event = create_test_event(
            wallet="0xtest",
            action="deposit_cex",
            size_frac=0.3
        )
        
        # Process through pipeline
        analysis = await analyze_event(event)
        assert analysis.classification == "bearish_signal"
        
        trade = await generate_trade(analysis)
        assert trade.side == "SHORT"
        
        validated = await validate_trade(trade)
        assert validated.approved == True
        
        order = await place_order(validated)
        assert order.status == "pending"
Level 3: End-to-End Tests (10%)
Full system flows
python# tests/e2e/test_full_cycle.py
class TestFullCycle:
    def test_complete_trade_cycle(self, test_client):
        # 1. Add wallet
        response = test_client.post("/v1/wallets", json={
            "address": "0xwhale",
            "label": "Test Whale"
        })
        assert response.status_code == 201
        
        # 2. Simulate incoming event
        webhook_data = {
            "wallet": "0xwhale",
            "type": "transfer",
            "amount": 1000
        }
        response = test_client.post("/webhook/alchemy", json=webhook_data)
        assert response.status_code == 200
        
        # 3. Check bias update
        response = test_client.get("/v1/bias")
        assert response.json()["ETH"] != 0
        
        # 4. Verify order creation
        response = test_client.get("/v1/orders")
        assert len(response.json()) > 0
Specialized Testing
Market Condition Scenarios
python# tests/scenarios/test_market_conditions.py
@pytest.mark.parametrize("scenario", [
    "bull_trend",
    "bear_trend",
    "high_volatility",
    "flash_crash",
    "low_liquidity"
])
def test_strategy_under_conditions(scenario, backtester):
    """
    Test strategy performance under different market conditions
    """
    data = load_scenario_data(scenario)
    results = backtester.run(
        strategy=TradingStrategy(),
        data=data,
        initial_capital=10000
    )
    
    # Scenario-specific assertions
    if scenario == "flash_crash":
        assert results.max_drawdown < 0.10  # Limit losses
    elif scenario == "bull_trend":
        assert results.total_return > 0     # Should be profitable
    
    # Universal checks
    assert results.risk_adjusted_return > 0
    assert results.win_rate > 0.4
Whale Behavior Patterns
python# tests/scenarios/test_whale_behaviors.py
class TestWhaleBehaviors:
    scenarios = [
        {
            "name": "coordinated_dump",
            "events": [
                {"wallet": "0x1", "action": "deposit_cex", "amount": 1000},
                {"wallet": "0x2", "action": "deposit_cex", "amount": 2000},
                {"wallet": "0x3", "action": "deposit_cex", "amount": 1500}
            ],
            "expected_bias": -0.8
        },
        {
            "name": "accumulation",
            "events": [
                {"wallet": "0x1", "action": "withdraw_cex", "amount": 500},
                {"wallet": "0x1", "action": "withdraw_cex", "amount": 500},
                {"wallet": "0x1", "action": "withdraw_cex", "amount": 500}
            ],
            "expected_bias": 0.6
        }
    ]
    
    @pytest.mark.parametrize("scenario", scenarios)
    def test_whale_scenario(self, scenario):
        bias = process_event_sequence(scenario["events"])
        assert abs(bias - scenario["expected_bias"]) < 0.1
Failure Mode Testing
python# tests/reliability/test_failure_modes.py
class TestFailureModes:
    def test_llm_timeout_fallback(self, mocker):
        # Mock LLM timeout
        mocker.patch('services.llm.analyze', side_effect=TimeoutError)
        
        # Should fallback to rule-based
        result = process_event_with_fallback(test_event)
        assert result.source == "rule_based"
        assert result.confidence < 0.7  # Lower confidence
    
    def test_exchange_api_failure(self):
        with mock_okx_failure():
            order = attempt_order_placement(test_order)
            assert order.status == "queued"
            assert order.retry_count == 1
    
    def test_database_connection_loss(self):
        with simulate_db_outage():
            # Should use cache
            result = get_wallet_scores("0xtest")
            assert result.source == "redis_cache"
    
    def test_websocket_reconnection(self):
        ws = WebSocketManager()
        
        # Simulate disconnect
        ws.disconnect()
        assert ws.connected == False
        
        # Wait for auto-reconnect
        time.sleep(5)
        assert ws.connected == True
        assert ws.reconnect_count == 1
Performance Testing
Load Testing
python# tests/performance/test_load.py
class TestLoad:
    def test_event_processing_throughput(self):
        """
        Requirement: 100 events/second
        """
        events = generate_test_events(count=1000)
        
        start_time = time.time()
        for event in events:
            process_event(event)
        duration = time.time() - start_time
        
        throughput = 1000 / duration
        assert throughput >= 100  # events/second
    
    def test_concurrent_orders(self):
        """
        Test concurrent order processing
        """
        orders = [generate_test_order() for _ in range(50)]
        
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(place_order, order) 
                      for order in orders]
            results = [f.result(timeout=10) for f in futures]
        
        assert all(r.status in ["success", "queued"] for r in results)
        assert len(set(r.client_order_id for r in results)) == 50  # All unique
Memory Leak Detection
python# tests/performance/test_memory.py
import tracemalloc

class TestMemory:
    def test_event_processing_memory(self):
        tracemalloc.start()
        
        # Process many events
        for _ in range(10000):
            process_event(generate_test_event())
        
        current, peak = tracemalloc.get_traced_memory()
        tracemalloc.stop()
        
        # Memory should not grow unbounded
        assert peak / current < 1.5  # Peak less than 1.5x current
        assert current < 100 * 1024 * 1024  # Less than 100MB
Security Testing
python# tests/security/test_security.py
class TestSecurity:
    def test_sql_injection(self):
        """
        Test SQL injection prevention
        """
        malicious_input = "'; DROP TABLE users; --"
        response = test_client.post("/v1/wallets", json={
            "address": malicious_input
        })
        
        # Should handle safely
        assert response.status_code in [400, 422]
        assert "users" in db.get_tables()  # Table still exists
    
    def test_rate_limiting(self):
        """
        Test rate limit enforcement
        """
        for i in range(12):  # Over limit of 10
            response = test_client.get("/v1/positions")
            
            if i < 10:
                assert response.status_code == 200
            else:
                assert response.status_code == 429  # Too many requests
    
    def test_api_key_rotation(self):
        """
        Test API key security
        """
        old_key = get_current_api_key()
        rotate_api_keys()
        new_key = get_current_api_key()
        
        assert old_key != new_key
        
        # Old key should still work during grace period
        response = make_request_with_key(old_key)
        assert response.status_code == 200
