# Monitoring & Observability

## Metrics Collection

### Business Metrics
```yaml
trading_metrics:
  - metric: total_pnl
    type: gauge
    labels: [mode, asset]
    alert: < -1000 over 1h
    
  - metric: win_rate
    type: gauge
    labels: [mode, timeframe]
    alert: < 0.4 over 24h
    
  - metric: positions_opened
    type: counter
    labels: [mode, asset, side]
    
  - metric: average_hold_time
    type: histogram
    buckets: [1m, 5m, 15m, 1h, 4h, 24h]
    
whale_metrics:
  - metric: events_processed
    type: counter
    labels: [wallet, event_type]
    
  - metric: wallet_credibility
    type: gauge
    labels: [wallet]
    
  - metric: bias_value
    type: gauge
    labels: [asset, timeframe]
System Metrics
yamlinfrastructure:
  - metric: api_latency
    type: histogram
    labels: [endpoint, method]
    slo: p99 < 500ms
    
  - metric: websocket_status
    type: gauge
    values: [0: disconnected, 1: connected]
    alert: == 0 for 2m
    
  - metric: database_connections
    type: gauge
    alert: > 80% of max
    
  - metric: redis_memory_usage
    type: gauge
    alert: > 90% of limit
    
llm_metrics:
  - metric: llm_requests
    type: counter
    labels: [model, purpose]
    
  - metric: llm_latency
    type: histogram
    labels: [model]
    alert: p95 > 5s
    
  - metric: llm_cost
    type: counter
    labels: [model]
    alert: > $8 per day
Dashboards
Main Trading Dashboard
json{
  "panels": [
    {
      "title": "P&L Overview",
      "type": "timeseries",
      "queries": [
        "sum(realized_pnl) by (mode)",
        "sum(unrealized_pnl) by (asset)"
      ]
    },
    {
      "title": "Position Status",
      "type": "stat",
      "queries": [
        "count(open_positions)",
        "sum(risk_consumed)",
        "current_drawdown"
      ]
    },
    {
      "title": "Whale Activity",
      "type": "heatmap",
      "query": "rate(events_processed[5m]) by (wallet)"
    },
    {
      "title": "Bias Tracker",
      "type": "gauge",
      "queries": [
        "bias_value{asset='BTC'}",
        "bias_value{asset='ETH'}"
      ]
    }
  ]
}
Risk Dashboard
json{
  "panels": [
    {
      "title": "Risk Utilization",
      "type": "gauge",
      "query": "risk_consumed / risk_limit",
      "thresholds": [
        {"value": 0.5, "color": "green"},
        {"value": 0.8, "color": "yellow"},
        {"value": 0.9, "color": "red"}
      ]
    },
    {
      "title": "Drawdown History",
      "type": "timeseries",
      "query": "max_drawdown[24h]"
    },
    {
      "title": "VaR (95%)",
      "type": "stat",
      "query": "value_at_risk_95"
    }
  ]
}
Alerting Rules
Critical Alerts
yamlcritical_alerts:
  - name: TradingHalted
    condition: trading_active == 0
    for: 1m
    notify: [pagerduty, slack]
    
  - name: SevereDrawdown
    condition: current_drawdown > 5%
    for: 0m
    notify: [pagerduty, slack, email]
    
  - name: ExchangeAPIDown
    condition: okx_api_health == 0
    for: 2m
    notify: [pagerduty, slack]
    
  - name: DatabaseDown
    condition: up{job="postgres"} == 0
    for: 1m
    notify: [pagerduty]
Warning Alerts
yamlwarning_alerts:
  - name: HighLLMCost
    condition: sum(llm_cost[1h]) > 1
    notify: [slack]
    
  - name: LowWinRate
    condition: win_rate < 0.45
    for: 4h
    notify: [email]
    
  - name: WebSocketReconnects
    condition: rate(ws_reconnects[5m]) > 0.2
    notify: [slack]
Logging Strategy
Structured Logging
pythonimport structlog

logger = structlog.get_logger()

# Trading events
logger.info(
    "position_opened",
    position_id=position.id,
    asset=position.asset,
    side=position.side,
    size=position.size,
    entry_price=position.entry_price,
    signal_wallet=position.signal_wallet,
    trace_id=context.trace_id
)

# Error logging
logger.error(
    "order_failed",
    order_id=order.id,
    error=str(e),
    retry_count=retry_count,
    trace_id=context.trace_id,
    exc_info=True
)
Log Aggregation
yamllog_pipeline:
  sources:
    - api: /var/log/api/*.log
    - workers: /var/log/workers/*.log
    - trading: /var/log/trading/*.log
    
  processing:
    - parse: json
    - enrich: 
        - geoip
        - user_agent
    - filter: level >= INFO
    
  destinations:
    - elasticsearch:
        index: logs-{yyyy.MM.dd}
    - s3:
        bucket: trading-logs
        prefix: raw/
Distributed Tracing
Trace Configuration
pythonfrom opentelemetry import trace
from opentelemetry.exporter.otlp import OTLPSpanExporter

tracer = trace.get_tracer(__name__)

@tracer.start_as_current_span("process_whale_event")
def process_whale_event(event):
    span = trace.get_current_span()
    span.set_attribute("event.wallet", event.wallet)
    span.set_attribute("event.type", event.type)
    span.set_attribute("event.size_frac", event.size_frac)
    
    with tracer.start_as_current_span("analyze_event"):
        analysis = llm_analyze(event)
    
    with tracer.start_as_current_span("update_bias"):
        bias = update_bias(analysis)
    
    with tracer.start_as_current_span("check_trading_signal"):
        signal = generate_signal(bias)
    
    return signal
Health Checks
Service Health Endpoints
python@app.get("/health")
def health_check():
    checks = {
        "database": check_database(),
        "redis": check_redis(),
        "exchange_api": check_okx(),
        "websocket": check_websocket(),
        "llm_api": check_groq()
    }
    
    status = "healthy" if all(checks.values()) else "unhealthy"
    
    return {
        "status": status,
        "checks": checks,
        "timestamp": datetime.now(),
        "version": APP_VERSION
    }

@app.get("/ready")
def readiness_check():
    return {
        "ready": is_initialized() and not is_kill_switch_active(),
        "mode": TRADING_MODE,
        "uptime": get_uptime()
    }
Performance Monitoring
Query Performance
sql-- Slow query log
CREATE EXTENSION IF NOT EXISTS pg_stat_statements;

-- Monitor slow queries
SELECT 
    query,
    mean_exec_time,
    calls,
    total_exec_time
FROM pg_stat_statements
WHERE mean_exec_time > 100  -- ms
ORDER BY mean_exec_time DESC
LIMIT 10;
Application Profiling
pythonimport cProfile
import pstats
from functools import wraps

def profile_critical_path(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        profiler = cProfile.Profile()
        profiler.enable()
        
        result = func(*args, **kwargs)
        
        profiler.disable()
        stats = pstats.Stats(profiler)
        stats.sort_stats('cumulative')
        
        # Log if slow
        if stats.total_tt > 1.0:  # seconds
            logger.warning(
                "slow_function",
                function=func.__name__,
                total_time=stats.total_tt
            )
        
        return result
    return wrapper

### **docs/Deployment.md** (Yeni)
```markdown
# Deployment Guide

## Infrastructure Setup

### Prerequisites
```bash
# Required tools
- Docker 24.0+
- Docker Compose 2.20+
- Node.js 20+
- Python 3.11+
- PostgreSQL client 15+
- Redis client 7+
Environment Setup
bash# Clone repository
git clone https://github.com/yourorg/whale-trader.git
cd whale-trader

# Setup environments
cp .env.example .env.development
cp .env.example .env.staging
cp .env.example .env.production

# Install dependencies
npm install
pip install -r requirements.txt
Docker Configuration
docker-compose.yml
yamlversion: '3.9'

services:
  postgres:
    image: timescale/timescaledb:latest-pg15
    environment:
      POSTGRES_DB: trading
      POSTGRES_USER: trader
      POSTGRES_PASSWORD: ${DB_PASSWORD}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"
    
  redis:
    image: redis:7-alpine
    command: redis-server --appendonly yes
    volumes:
      - redis_data:/data
    ports:
      - "6379:6379"
    
  api:
    build:
      context: ./services/api
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/trading
      REDIS_URL: redis://redis:6379
      TRADING_MODE: ${TRADING_MODE}
    depends_on:
      - postgres
      - redis
    ports:
      - "8000:8000"
    
  order-manager:
    build:
      context: ./services/order-manager
      dockerfile: Dockerfile
    environment:
      DATABASE_URL: postgresql://trader:${DB_PASSWORD}@postgres:5432/trading
      OKX_MODE: ${OKX_MODE}
    depends_on:
      - postgres
      - api
    
  web:
    build:
      context: ./apps/web
      dockerfile: Dockerfile
    environment:
      NEXT_PUBLIC_API_URL: ${API_URL}
    ports:
      - "3000:3000"

volumes:
  postgres_data:
  redis_data:
Cloudflare Deployment
Workers Configuration
javascript// wrangler.toml
name = "whale-trader-worker"
main = "src/index.js"
compatibility_date = "2024-01-01"

[env.production]
vars = { ENVIRONMENT = "production" }
kv_namespaces = [
  { binding = "CACHE", id = "xxx" }
]

[env.staging]
vars = { ENVIRONMENT = "staging" }

[[r2_buckets]]
binding = "STORAGE"
bucket_name = "whale-trader-storage"
Pages Deployment
bash# Build Next.js app
npm run build

# Deploy to Cloudflare Pages
npx wrangler pages deploy out \
  --project-name=whale-trader \
  --branch=main
Database Migrations
Initial Setup
sql-- migrations/001_initial.sql
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

-- Create tables
\i migrations/tables/users.sql
\i migrations/tables/wallets.sql
\i migrations/tables/events.sql
\i migrations/tables/orders.sql
\i migrations/tables/positions.sql

-- Create hypertables
SELECT create_hypertable('events', 'timestamp');
SELECT create_hypertable('wallet_scores', 'timestamp');
SELECT create_hypertable('bias', 'timestamp');

-- Create indexes
\i migrations/indexes/indexes.sql
Migration Script
bash#!/bin/bash
# scripts/migrate.sh

set -e

ENV=${1:-development}

echo "Running migrations for: $ENV"

if [ "$ENV" == "production" ]; then
    read -p "Are you sure you want to run migrations on PRODUCTION? (yes/no): " confirm
    if [ "$confirm" != "yes" ]; then
        exit 1
    fi
fi

source .env.$ENV

psql $DATABASE_URL -f migrations/001_initial.sql
psql $DATABASE_URL -f migrations/002_functions.sql
psql $DATABASE_URL -f migrations/003_views.sql

echo "Migrations completed successfully"
CI/CD Pipeline
GitHub Actions
yaml# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches:
      - main
      - staging

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Run tests
        run: |
          pip install -r requirements-dev.txt
          pytest --cov=services
      
      - name: Security scan
        run: |
          pip install safety bandit
          safety check
          bandit -r services/
  
  deploy-staging:
    needs: test
    if: github.ref == 'refs/heads/staging'
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to staging
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
        run: |
          npm run build
          npx wrangler deploy --env staging
  
  deploy-production:
    needs: test
    if: github.ref == 'refs/heads/main'
    runs-on: ubuntu-latest
    environment:
      name: production
      url: https://whale-trader.com
    steps:
      - uses: actions/checkout@v3
      
      - name: Deploy to production
        env:
          CLOUDFLARE_API_TOKEN: ${{ secrets.CF_API_TOKEN }}
        run: |
          npm run build
          npx wrangler deploy --env production
Deployment Checklist
Pre-deployment
markdown- [ ] All tests passing
- [ ] Security scan completed
- [ ] Database migrations tested
- [ ] Environment variables configured
- [ ] API keys rotated
- [ ] Backup created
- [ ] Rollback plan prepared
Deployment Steps
markdown1. [ ] Set maintenance mode
2. [ ] Deploy database migrations
3. [ ] Deploy backend services
4. [ ] Deploy workers
5. [ ] Deploy frontend
6. [ ] Verify health checks
7. [ ] Run smoke tests
8. [ ] Monitor for 15 minutes
9. [ ] Remove maintenance mode
Post-deployment
markdown- [ ] Verify all services healthy
- [ ] Check error rates
- [ ] Monitor performance metrics
- [ ] Verify trading operations
- [ ] Update documentation
- [ ] Notify team
Rollback Procedures
Automatic Rollback
pythonclass DeploymentMonitor:
    def check_deployment_health(self):
        metrics = {
            "error_rate": get_error_rate(),
            "response_time": get_p99_latency(),
            "success_rate": get_success_rate()
        }
        
        if metrics["error_rate"] > 0.05:  # 5% error rate
            self.trigger_rollback("High error rate")
        elif metrics["response_time"] > 2000:  # 2s P99
            self.trigger_rollback("High latency")
        elif metrics["success_rate"] < 0.95:  # 95% success
            self.trigger_rollback("Low success rate")
    
    def trigger_rollback(self, reason):
        logger.critical(f"Triggering rollback: {reason}")
        
        # Rollback steps
        self.switch_traffic_to_previous()
        self.restore_database_if_needed()
        self.clear_caches()
        self.notify_team(reason)
Manual Rollback
bash#!/bin/bash
# scripts/rollback.sh

PREVIOUS_VERSION=$1

if [ -z "$PREVIOUS_VERSION" ]; then
    echo "Usage: ./rollback.sh <version>"
    exit 1
fi

echo "Rolling back to version: $PREVIOUS_VERSION"

# Stop current services
docker-compose down

# Checkout previous version
git checkout $PREVIOUS_VERSION

# Restore database backup if needed
if [ -f "backups/db-$PREVIOUS_VERSION.sql" ]; then
    psql $DATABASE_URL < backups/db-$PREVIOUS_VERSION.sql
fi

# Restart services
docker-compose up -d

echo "Rollback completed"
Monitoring Post-Deployment
bash# scripts/post-deploy-check.sh
#!/bin/bash

echo "Running post-deployment checks..."

# Check service health
curl -f http://api.whale-trader.com/health || exit 1

# Check critical endpoints
curl -f http://api.whale-trader.com/v1/bias || exit 1

# Check WebSocket connection
wscat -c wss://api.whale-trader.com/ws || exit 1

# Check database connectivity
psql $DATABASE_URL -c "SELECT 1" || exit 1

# Check Redis
redis-cli ping || exit 1

echo "All checks passed!"

## 📝 ADIM 3: ENV DOSYALARI

### **.env.example**
```bash
# Environment
NODE_ENV=development
PYTHON_ENV=development
TRADING_MODE=demo

# Database
DATABASE_URL=postgresql://trader:password@localhost:5432/trading

# Redis
REDIS_URL=redis://localhost:6379

# LLM (Groq)
GROQ_API_KEY=gsk_xxxxxxxxxxxxxxxxxxxx
GROQ_MODEL=llama-4.3-70b-instruct
GROQ_DAILY_BUDGET=10.0

# Blockchain
ALCHEMY_API_KEY=xxxxxxxxxxxxxxxxxxxxx
ALCHEMY_WS_URL=wss://eth-mainnet.g.alchemy.com/v2/
ETHERSCAN_API_KEY=xxxxxxxxxxxxxxxxxxxxx

# OKX Trading
OKX_MODE=demo
OKX_API_KEY=xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx
OKX_API_SECRET=XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
OKX_API_PASSPHRASE=YourPassphrase
OKX_SIMULATED_TRADING=1

# Risk Limits
MAX_POSITION_SIZE=0.0025
MAX_DAILY_LOSS=0.03
MAX_LEVERAGE=3

# Authentication
JWT_SECRET=your-secret-key-change-this
JWT_EXPIRES_IN=3600
REFRESH_TOKEN_EXPIRES_IN=604800

# Web Push
VAPID_PUBLIC_KEY=xxxxxxxxxxxxxxxxxxxxx
VAPID_PRIVATE_KEY=xxxxxxxxxxxxxxxxxxxxx
PUSH_CONTACT=mailto:admin@whale-trader.com

# Monitoring
SENTRY_DSN=https://xxxxx@sentry.io/xxxxx
LOG_LEVEL=info

# Feature Flags
ENABLE_PAPER_TRADING=true
ENABLE_LIVE_TRADING=false
ENABLE_LLM_ANALYSIS=true
ENABLE_BACKTESTING=true
