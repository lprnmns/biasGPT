# LLM Cost Optimization Strategy

## Overview
Target: < $10/day while maintaining decision quality

## Intelligent Triggering System

### Event Filtering Pipeline
```pythonclass LLMTriggerDecision:
"""
Multi-stage filter to minimize unnecessary LLM calls
"""def should_trigger_llm(self, event: Event) -> bool:
    # Stage 1: Hard filters (No LLM needed)
    if not self._passes_basic_filters(event):
        return False    # Stage 2: Pattern matching (No LLM needed)
    if self._matches_known_pattern(event):
        self._apply_cached_decision(event)
        return False    # Stage 3: Rate limiting
    if self._exceeds_rate_limit():
        return event.size_frac > 0.30  # Only critical events    # Stage 4: Cost-benefit analysis
    return self._expected_value(event) > LLM_COSTdef _passes_basic_filters(self, event):
    return (
        event.size_frac >= 0.10 and
        event.wallet_credibility >= 3.0 and
        event.notional_usd >= 50000
    )def _matches_known_pattern(self, event):
    # Check against pattern library
    patterns = [
        "cex_deposit_before_dump",
        "accumulation_pattern",
        "bridge_activity"
    ]
    return PatternMatcher.match(event, patterns)

### Caching Strategy

#### Pattern Library
```pythonCACHED_PATTERNS = {
"whale_cex_deposit": {
"conditions": {
"action": "deposit_cex",
"size_frac": "> 0.25",
"wallet_credibility": "> 6"
},
"decision": {
"bias_adjustment": -0.2,
"confidence": 0.75,
"action": "PREPARE_SHORT"
},
"ttl": 3600  # 1 hour cache
}
}

#### Semantic Caching with Embeddings
```sql-- Using pgvector for similarity search
CREATE TABLE llm_cache (
id SERIAL PRIMARY KEY,
event_embedding vector(768),
response JSONB,
created_at TIMESTAMP,
usage_count INT DEFAULT 1
);-- Find similar past events
SELECT response FROM llm_cache
WHERE event_embedding <-> $1 < 0.1  -- Cosine similarity
ORDER BY event_embedding <-> $1
LIMIT 1;

## Batch Processing

### Micro-batching Strategy
```pythonclass LLMBatcher:
def init(self, batch_size=5, wait_time=2.0):
self.pending = []
self.batch_size = batch_size
self.wait_time = wait_timeasync def add_event(self, event):
    self.pending.append(event)    if len(self.pending) >= self.batch_size:
        return await self._process_batch()    # Wait for more events or timeout
    await asyncio.sleep(self.wait_time)
    if self.pending:
        return await self._process_batch()async def _process_batch(self):
    # Single LLM call for multiple events
    prompt = self._build_batch_prompt(self.pending)
    response = await llm.analyze_batch(prompt)
    self.pending.clear()
    return response

## Token Optimization

### Prompt Compression
```pythondef compress_context(events: List[Event]) -> str:
"""
Reduce token count while preserving information
"""
# Remove redundant fields
essential_fields = ['wallet', 'action', 'asset', 'size_frac', 'notional_usd']# Aggregate similar events
aggregated = defaultdict(list)
for event in events:
    key = (event.wallet, event.action, event.asset)
    aggregated[key].append(event.size_frac)# Format compressed
compressed = []
for (wallet, action, asset), sizes in aggregated.items():
    compressed.append(f"{wallet[:8]}:{action}:{asset}:{sum(sizes):.2f}")return "\n".join(compressed)

### Response Format Optimization
```pythonRESPONSE_SCHEMA = {
"type": "object",
"properties": {
"c": {"type": "string", "maxLength": 20},  # classification
"s": {"type": "number", "minimum": 0, "maximum": 1},  # score
"a": {"type": "string", "enum": ["L", "S", "N"]},  # Long/Short/None
"r": {"type": "string", "maxLength": 100}  # reasoning
},
"required": ["c", "s", "a"],
"additionalProperties": False
}

## Model Selection Strategy

### Tiered Model Approach
```pythonMODEL_TIERS = {
"critical": {  # High-value decisions
"model": "llama-4-maverick-17b-128e-instruct",
"temperature": 0.1,
"max_tokens": 500
},
"standard": {  # Regular analysis
"model": "llama-3.3-70b-versatile",
"temperature": 0.3,
"max_tokens": 200
},
"simple": {  # Pattern matching
"model": "llama-3.2-3b-preview",
"temperature": 0.5,
"max_tokens": 100
}
}def select_model_tier(event):
if event.notional_usd > 1_000_000:
return MODEL_TIERS["critical"]
elif event.size_frac > 0.20:
return MODEL_TIERS["standard"]
else:
return MODEL_TIERS["simple"]

## Cost Monitoring

### Real-time Budget Tracking
```pythonclass LLMBudgetManager:
def init(self, daily_limit=10.0):
self.daily_limit = daily_limit
self.current_spend = 0.0
self.reset_time = Nonedef can_call(self, estimated_cost):
    if self.current_spend + estimated_cost > self.daily_limit:
        logger.warning(f"LLM budget exceeded: ${self.current_spend:.2f}")
        return False
    return Truedef track_usage(self, tokens_used, model):
    cost = self.calculate_cost(tokens_used, model)
    self.current_spend += cost    # Alert if approaching limit
    if self.current_spend > self.daily_limit * 0.8:
        send_alert(f"LLM budget at 80%: ${self.current_spend:.2f}")

### Cost Analytics Dashboard
```sql-- Daily LLM usage analysis
CREATE VIEW llm_cost_analytics AS
SELECT
DATE(timestamp) as date,
COUNT(*) as total_calls,
SUM(tokens_used) as total_tokens,
SUM(cost_usd) as total_cost,
AVG(response_quality_score) as avg_quality,
SUM(CASE WHEN resulted_in_trade THEN cost_usd ELSE 0 END) /
NULLIF(SUM(cost_usd), 0) as roi
FROM llm_calls
GROUP BY DATE(timestamp);

## Fallback Strategies

### When LLM Unavailable or Over Budget
```pythonclass RuleBasedFallback:
"""
Deterministic rules when LLM is unavailable
"""def analyze(self, event):
    score = 0.5  # Neutral baseline    # Size impact
    if event.size_frac > 0.30:
        score *= 1.5    # Credibility weight
    score *= (event.wallet_credibility / 10)    # Action type bias
    action_weights = {
        "deposit_cex": -0.2,  # Bearish
        "withdraw_cex": 0.1,   # Slightly bullish
        "accumulation": 0.3    # Bullish
    }    if event.action in action_weights:
        score += action_weights[event.action]    return {
        "confidence": min(score, 1.0),
        "source": "rule_based_fallback"
    }

## Optimization Metrics

### Key Performance Indicators
- Cost per decision: < $0.02
- Cache hit rate: > 60%
- Batch efficiency: > 3 events/call
- Pattern library coverage: > 40%
- Fallback usage: < 10%
