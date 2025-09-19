# Architecture
# System Architecture

## 1. High-Level Architecture┌─────────────────────────────────────────────────────────┐
│                        USER LAYER                        │
│  ┌──────────┐  ┌──────────┐  ┌──────────┐              │
│  │   PWA    │  │   Chat   │  │   Push   │              │
│  └──────────┘  └──────────┘  └──────────┘              │
└─────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────┐
│                     GATEWAY LAYER                        │
│  ┌──────────────────────────────────────────────────┐  │
│  │          Cloudflare Workers (Edge)               │  │
│  │  - Rate Limiting                                 │  │
│  │  - Request Routing                               │  │
│  │  - WebSocket Proxy                               │  │
│  └──────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────┐
│                    PROCESSING LAYER                      │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │  Ingest   │  │  Scoring  │  │    LLM    │          │
│  │  Worker   │→ │  Engine   │→ │   Brain   │          │
│  └───────────┘  └───────────┘  └───────────┘          │
│         ↓              ↓              ↓                 │
│  ┌──────────────────────────────────────────┐          │
│  │         Event Queue (Redis)              │          │
│  └──────────────────────────────────────────┘          │
└─────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────┐
│                    DECISION LAYER                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │   Bias    │  │  Policy   │  │   Risk    │          │
│  │  Calculator│→ │  Engine   │→ │  Manager  │          │
│  └───────────┘  └───────────┘  └───────────┘          │
└─────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────┐
│                   EXECUTION LAYER                        │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │   Order   │  │ Position  │  │  Report   │          │
│  │  Manager  │  │  Monitor  │  │ Generator │          │
│  └───────────┘  └───────────┘  └───────────┘          │
└─────────────────────────────────────────────────────────┘
│
┌─────────────────────────────────────────────────────────┐
│                     DATA LAYER                           │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐          │
│  │ PostgreSQL│  │   Redis   │  │   Blob    │          │
│  │   (Neon)  │  │ (Upstash) │  │  Storage  │          │
│  └───────────┘  └───────────┘  └───────────┘          │
└─────────────────────────────────────────────────────────┘

## 2. Component Details

### Frontend (apps/web)
- **Tech**: Next.js 14 with App Router
- **Deployment**: Cloudflare Pages
- **Features**: PWA, Web Push, WebSocket client
- **Auth**: JWT with refresh tokens

### Workers (workers/)
- **ingest**: Alchemy webhook handler, WebSocket client
- **cron**: Scheduled tasks (backfill, cleanup, reports)
- **proxy**: API gateway with rate limiting

### Services (services/)
- **api**: FastAPI main backend
- **order-manager**: OKX integration service
- **reporter**: Report generation and distribution
- **backtest**: Historical simulation engine

### Data Flow
1. **Event Ingestion**
   - Alchemy WS → Ingest Worker → Event Queue → API
   - Fallback: Etherscan REST API polling

2. **Processing Pipeline**Event → Normalize → Feature Extract → Score → Bias Update
↓
LLM Analysis (conditional)
↓
Policy Check → Order

3. **Order Lifecycle**Signal → Risk Check → Size Calculation → Order Placement
↓
Monitor → Close → Report

## 3. Environment Configuration

### Development
- Local PostgreSQL + Redis
- OKX Demo API
- Mock LLM responses
- Hot reload enabled

### Staging  
- Neon PostgreSQL + Upstash Redis
- OKX Paper Trading
- Real LLM with rate limits
- Monitoring enabled

### Production
- Same as staging +
- OKX Live Trading
- Multi-region deployment
- Full observability

## 4. Scalability Considerations

### Current (MVP)
- Single region deployment
- Synchronous processing
- 100 events/sec capacity

### Future (v2)
- Multi-region with edge workers
- Async event processing with Kafka
- Horizontal scaling with Kubernetes
- 10,000 events/sec capacity
