# FinPred — Multi-Agent AI Market Sentiment Simulator

FinPred is a multi-agent simulation engine that forecasts US market sentiment by orchestrating AI-powered agents with distinct financial personas. Agents interact on simulated social feeds (Twitter/Reddit), react to live commodity prices (Oil, Gold, Silver), influence each other's sentiment, and produce real-time analytics on price impact, stance ratios, and emergent market narratives.

## How It Works

1. **Create a scenario** — define a seed event (e.g., "OPEC+ announces emergency production cut"), environment parameters, and agent count.
2. **Agents are generated** — distributed across 5 persona types with realistic behaviors.
3. **Live market data loads** — real-time Oil (WTI), Gold, and Silver futures prices are fetched via yfinance and injected into agent feeds.
4. **Simulation runs tick-by-tick** — each tick, agents read their personalized feed (including commodity prices), post/comment, and shift sentiment based on social influence.
5. **Live analytics stream** via WebSocket — price impact, stance ratios, per-persona sentiment, commodity context.
6. **Post-simulation analysis** — emergent narratives, top influencers, and optional B2B PDF reports.

## Agent Personas

| Persona | Share | Behavior |
|---------|-------|----------|
| Retail Trader | 35% | FOMO-driven, reactive to social sentiment, commodity hype |
| HFT Algorithm | 20% | Data-driven, reacts to commodity price signals and momentum |
| Institutional Investor | 20% | Fundamentals-focused, monitors commodity allocation and inflation |
| Macro Hedge Fund | 15% | Fed/policy-focused, trades oil-dollar-gold correlations |
| Finfluencer | 10% | Attention-seeking, drives retail behavior on commodity plays |

## Live Commodity Prices

FinPred fetches real-time futures prices using **yfinance** (no API key required):

| Commodity | Ticker | How Agents Use It |
|-----------|--------|-------------------|
| WTI Crude Oil | `CL=F` | HFT, institutional, and macro agents see price + change in their feeds |
| Gold | `GC=F` | Macro agents trade dollar-gold inverse; retail follows finfluencer gold calls |
| Silver | `SI=F` | Retail coordinates squeeze plays; institutional monitors gold-silver ratio |

The `/commodities` page provides interactive price charts with 1W/1M/3M/6M/1Y history.

## Tech Stack

**Backend** — Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Alembic
**AI/LLM** — OpenAI GPT-4o-mini (agents), Anthropic Claude (reports), CAMEL-AI, Zep Cloud (memory)
**Market Data** — yfinance (Oil, Gold, Silver futures)
**Frontend** — Nuxt 3, Vue 3, Chart.js
**DevOps** — Docker Compose

## Quick Start

### 1. Clone & configure

```bash
git clone https://github.com/itsnkr22/FinPred.git
cd FinPred
cp .env.example .env
```

Edit `.env` and add your API keys:

```
OPENAI_API_KEY=sk-...          # Agent simulation
ANTHROPIC_API_KEY=sk-ant-...   # Report generation
ZEP_API_KEY=z_...              # Agent memory (optional)
```

> Commodity prices (Oil, Gold, Silver) are fetched via yfinance — no API key needed.

### 2. Run with Docker

```bash
docker-compose up
```

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

### 3. Or run manually

**Backend:**
```bash
cd backend
pip install -r requirements.txt
alembic upgrade head
python ../scripts/seed_db.py        # optional: seed sample scenarios
uvicorn app.main:app --reload --port 8000
```

**Frontend:**
```bash
cd frontend
npm install
npm run dev
```

### 4. CLI mode (no frontend)

```bash
python scripts/run_sim_cli.py "Federal Reserve announces emergency rate cut"
```

## Sample Scenarios

| Scenario | Sector | Volatility |
|----------|--------|------------|
| Fed Rate Cut Surprise | General | High |
| SEC Crypto Crackdown | Crypto | Extreme |
| NVIDIA Earnings Blowout | Tech | High |
| Oil Supply Shock (OPEC+ 2M bbl cut) | Commodities | Extreme |
| Gold Rush: Dollar Collapse Fear | Commodities | Extreme |
| Silver Squeeze 2.0 | Commodities | High |

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/api/v1/scenarios` | Create scenario |
| `GET` | `/api/v1/scenarios` | List scenarios |
| `POST` | `/api/v1/simulations/{id}/run` | Start simulation |
| `WS` | `/api/v1/simulations/{id}/ws` | Live tick stream |
| `GET` | `/api/v1/analytics/{id}` | Full results |
| `GET` | `/api/v1/analytics/{id}/narratives` | Emergent narratives |
| `POST` | `/api/v1/analytics/{id}/report` | Generate PDF report |
| `GET` | `/api/v1/commodities` | All commodity prices (Oil, Gold, Silver) |
| `GET` | `/api/v1/commodities/{commodity}` | Single commodity price |
| `GET` | `/api/v1/commodities/{commodity}/history` | Historical prices (1d–5y) |

Full interactive docs at `/docs` when the backend is running.

## Key Metrics

- **P_impact** — `sum(Sentiment_i x CapitalWeight_i)` — net bullish/bearish pressure
- **Stance Ratios** — BUY / SELL / HOLD percentages across all agents
- **Sentiment Timeline** — per-tick aggregate and per-persona sentiment tracking
- **Emergent Narratives** — detected social contagion patterns and institutional vs. retail divergence
- **Commodity Context** — real-time Oil/Gold/Silver prices fed to data-driven agent personas

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers (scenarios, simulations, commodities)
│   │   ├── engine/         # Simulation core (runner, personas, influence, metrics)
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic layer
│   │   ├── memory/         # Zep Cloud integration
│   │   └── ingestion/      # Data scrapers + commodity price fetcher (yfinance)
│   ├── alembic/            # Database migrations
│   └── tests/              # Test suite
├── frontend/
│   ├── pages/              # Nuxt pages (dashboard, scenarios, simulation, analytics, commodities)
│   ├── composables/        # Vue composables (useSimulation, useScenarios, useCommodities)
│   └── types/              # TypeScript definitions
├── scripts/                # CLI runner & DB seeder
├── docker-compose.yml
└── .env.example
```

## License

MIT
