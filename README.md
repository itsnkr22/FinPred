# FinPred — Multi-Agent AI Market Sentiment Simulator

FinPred is a multi-agent simulation engine that forecasts US market sentiment by orchestrating AI-powered agents with distinct financial personas. Agents interact on simulated social feeds (Twitter/Reddit), influence each other's sentiment, and produce real-time analytics on price impact, stance ratios, and emergent market narratives.

## How It Works

1. **Create a scenario** — define a seed event (e.g., "Fed announces emergency 50bp rate cut"), environment parameters, and agent count.
2. **Agents are generated** — distributed across 5 persona types with realistic behaviors.
3. **Simulation runs tick-by-tick** — each tick, agents read their personalized feed, post/comment, and shift sentiment based on social influence.
4. **Live analytics stream** via WebSocket — price impact, stance ratios, per-persona sentiment.
5. **Post-simulation analysis** — emergent narratives, top influencers, and optional B2B PDF reports.

## Agent Personas

| Persona | Share | Behavior |
|---------|-------|----------|
| Retail Trader | 35% | FOMO-driven, reactive to social sentiment |
| HFT Algorithm | 20% | Emotionless, data-driven, ignores social influence |
| Institutional Investor | 20% | Methodical, fundamentals-focused, high capital weight |
| Macro Hedge Fund | 15% | Fed/policy-focused, systemic risk analysis |
| Finfluencer | 10% | Attention-seeking, drives retail behavior, high influence |

## Tech Stack

**Backend** — Python 3.12, FastAPI, SQLAlchemy 2.0, PostgreSQL 16, Alembic
**AI/LLM** — OpenAI GPT-4o-mini (agents), Anthropic Claude (reports), CAMEL-AI, Zep Cloud (memory)
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

Full interactive docs at `/docs` when the backend is running.

## Key Metrics

- **P_impact** — `sum(Sentiment_i x CapitalWeight_i)` — net bullish/bearish pressure
- **Stance Ratios** — BUY / SELL / HOLD percentages across all agents
- **Sentiment Timeline** — per-tick aggregate and per-persona sentiment tracking
- **Emergent Narratives** — detected social contagion patterns and institutional vs. retail divergence

## Project Structure

```
├── backend/
│   ├── app/
│   │   ├── api/            # FastAPI route handlers
│   │   ├── engine/         # Simulation core (runner, personas, influence, metrics)
│   │   ├── models/         # SQLAlchemy ORM models
│   │   ├── schemas/        # Pydantic request/response schemas
│   │   ├── services/       # Business logic layer
│   │   ├── memory/         # Zep Cloud integration
│   │   └── ingestion/      # Data scrapers (news, Twitter, Reddit)
│   ├── alembic/            # Database migrations
│   └── tests/              # Test suite
├── frontend/
│   ├── pages/              # Nuxt pages (dashboard, scenarios, simulation, analytics)
│   ├── composables/        # Vue composables
│   └── types/              # TypeScript definitions
├── scripts/                # CLI runner & DB seeder
├── docker-compose.yml
└── .env.example
```

## License

MIT
