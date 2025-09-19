# Database Schema

## Core Tables

### users
```sqlCREATE TABLE users (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
email VARCHAR(255) UNIQUE NOT NULL,
password_hash VARCHAR(255) NOT NULL,
trading_mode VARCHAR(20) DEFAULT 'demo',
created_at TIMESTAMP DEFAULT NOW(),
updated_at TIMESTAMP DEFAULT NOW(),
last_login TIMESTAMP,
is_active BOOLEAN DEFAULT true,
two_fa_enabled BOOLEAN DEFAULT false,
two_fa_secret VARCHAR(255)
);CREATE INDEX idx_users_email ON users(email);

### wallets
```sqlCREATE TABLE wallets (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
address VARCHAR(42) UNIQUE NOT NULL,
label VARCHAR(100),
chain VARCHAR(20) DEFAULT 'ethereum',
first_seen_at TIMESTAMP DEFAULT NOW(),
last_activity TIMESTAMP,
is_active BOOLEAN DEFAULT true,
tags TEXT[],
metadata JSONB
);CREATE INDEX idx_wallets_address ON wallets(address);
CREATE INDEX idx_wallets_active ON wallets(is_active);

### wallet_scores
```sql-- TimescaleDB hypertable for time-series data
CREATE TABLE wallet_scores (
wallet_id UUID REFERENCES wallets(id),
timestamp TIMESTAMP NOT NULL,
credibility_1h DECIMAL(3,1),
credibility_4h DECIMAL(3,1),
credibility_24h DECIMAL(3,1),
equity_usd DECIMAL(20,2),
trading_volume_24h DECIMAL(20,2),
win_rate DECIMAL(3,2),
archetype VARCHAR(50)
);SELECT create_hypertable('wallet_scores', 'timestamp');
CREATE INDEX idx_wallet_scores_composite ON wallet_scores(wallet_id, timestamp DESC);

### events
```sqlCREATE TABLE events (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
timestamp TIMESTAMP NOT NULL,
wallet_id UUID REFERENCES wallets(id),
tx_hash VARCHAR(66) UNIQUE NOT NULL,
event_type VARCHAR(50) NOT NULL,
asset VARCHAR(20),
amount DECIMAL(30,10),
notional_usd DECIMAL(20,2),
size_fraction DECIMAL(5,4),
venue VARCHAR(50),
gas_price DECIMAL(20,10),
is_first_since_watch BOOLEAN DEFAULT false,
raw_data JSONB,
processed_at TIMESTAMP DEFAULT NOW()
);SELECT create_hypertable('events', 'timestamp');
CREATE INDEX idx_events_wallet ON events(wallet_id, timestamp DESC);
CREATE INDEX idx_events_type ON events(event_type);

### event_analysis
```sqlCREATE TABLE event_analysis (
event_id UUID REFERENCES events(id) PRIMARY KEY,
llm_classification VARCHAR(100),
llm_confidence DECIMAL(3,2),
llm_narrative TEXT,
pattern_matched VARCHAR(100),
bias_impact DECIMAL(4,3),
proposed_action JSONB,
created_at TIMESTAMP DEFAULT NOW()
);

### bias
```sqlCREATE TABLE bias (
timestamp TIMESTAMP NOT NULL,
asset VARCHAR(20) NOT NULL,
timeframe VARCHAR(10) NOT NULL,
value DECIMAL(4,3),
components JSONB,
confidence DECIMAL(3,2)
);SELECT create_hypertable('bias', 'timestamp');
CREATE INDEX idx_bias_asset ON bias(asset, timestamp DESC);

### orders
```sqlCREATE TABLE orders (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
created_at TIMESTAMP DEFAULT NOW(),
trading_mode VARCHAR(20) NOT NULL,
exchange VARCHAR(20) DEFAULT 'okx',
client_order_id VARCHAR(100) UNIQUE NOT NULL,
exchange_order_id VARCHAR(100),
asset VARCHAR(20) NOT NULL,
side VARCHAR(10) NOT NULL,
order_type VARCHAR(20) NOT NULL,
size DECIMAL(20,10),
price DECIMAL(20,10),
status VARCHAR(20) DEFAULT 'pending',
filled_size DECIMAL(20,10) DEFAULT 0,
avg_fill_price DECIMAL(20,10),
fees DECIMAL(20,10) DEFAULT 0,
stop_loss DECIMAL(20,10),
take_profit DECIMAL(20,10)[],
signal_event_id UUID REFERENCES events(id),
policy_snapshot JSONB,
error_message TEXT,
updated_at TIMESTAMP DEFAULT NOW()
);CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_client_id ON orders(client_order_id);

### positions
```sqlCREATE TABLE positions (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
opened_at TIMESTAMP DEFAULT NOW(),
closed_at TIMESTAMP,
trading_mode VARCHAR(20) NOT NULL,
asset VARCHAR(20) NOT NULL,
side VARCHAR(10) NOT NULL,
entry_price DECIMAL(20,10),
exit_price DECIMAL(20,10),
size DECIMAL(20,10),
leverage DECIMAL(4,2) DEFAULT 1,
unrealized_pnl DECIMAL(20,2),
realized_pnl DECIMAL(20,2),
fees_paid DECIMAL(20,2),
funding_paid DECIMAL(20,2),
max_drawdown DECIMAL(5,2),
holding_time INTERVAL,
risk_consumed DECIMAL(5,4),
signal_wallet_id UUID REFERENCES wallets(id)
);CREATE INDEX idx_positions_open ON positions(closed_at) WHERE closed_at IS NULL;

### reports
```sqlCREATE TABLE reports (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
period_start TIMESTAMP NOT NULL,
period_end TIMESTAMP NOT NULL,
report_type VARCHAR(20) DEFAULT '4h',
summary_markdown TEXT,
metrics JSONB,
notable_events JSONB,
delivered_at TIMESTAMP,
push_sent BOOLEAN DEFAULT false,
created_at TIMESTAMP DEFAULT NOW()
);CREATE INDEX idx_reports_period ON reports(period_end DESC);

### audit_logs
```sqlCREATE TABLE audit_logs (
id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
timestamp TIMESTAMP DEFAULT NOW(),
user_id UUID REFERENCES users(id),
action VARCHAR(100) NOT NULL,
entity_type VARCHAR(50),
entity_id UUID,
old_value JSONB,
new_value JSONB,
ip_address INET,
user_agent TEXT,
trace_id VARCHAR(100)
);CREATE INDEX idx_audit_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_trace ON audit_logs(trace_id);

## Views

### active_positions_view
```sqlCREATE VIEW active_positions_view AS
SELECT
p.*,
w.address as signal_wallet,
w.credibility_4h as wallet_credibility,
(SELECT value FROM bias WHERE asset = p.asset
ORDER BY timestamp DESC LIMIT 1) as current_bias
FROM positions p
LEFT JOIN wallets w ON p.signal_wallet_id = w.id
WHERE p.closed_at IS NULL;

### daily_performance_view
```sqlCREATE MATERIALIZED VIEW daily_performance
WITH (timescaledb.continuous) AS
SELECT
time_bucket('1 day', closed_at) AS date,
trading_mode,
COUNT() as total_trades,
SUM(CASE WHEN realized_pnl > 0 THEN 1 ELSE 0 END)::FLOAT /
NULLIF(COUNT(), 0) as win_rate,
SUM(realized_pnl) as total_pnl,
AVG(realized_pnl) as avg_pnl,
MAX(realized_pnl) as best_trade,
MIN(realized_pnl) as worst_trade,
AVG(holding_time) as avg_holding_time
FROM positions
WHERE closed_at IS NOT NULL
GROUP BY date, trading_mode;

## Data Retention Policies
```sql-- Keep raw events for 90 days
SELECT add_retention_policy('events', INTERVAL '90 days');-- Keep wallet scores for 180 days
SELECT add_retention_policy('wallet_scores', INTERVAL '180 days');-- Keep bias for 30 days
SELECT add_retention_policy('bias', INTERVAL '30 days');-- Archive old positions
CREATE TABLE positions_archive (LIKE positions INCLUDING ALL);

## Migration Scripts
```sql-- V1: Initial schema
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "timescaledb";
CREATE EXTENSION IF NOT EXISTS "pgcrypto";-- V2: Add vector support for embeddings (future)
CREATE EXTENSION IF NOT EXISTS "vector";ALTER TABLE event_analysis
ADD COLUMN embedding vector(768);
