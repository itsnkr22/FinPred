"""Mock market data for MVP testing."""

from datetime import datetime


def get_mock_market_data() -> list[dict]:
    """Return realistic mock market data items for seeding simulations."""
    return [
        {
            "source": "bloomberg",
            "content": "Federal Reserve signals potential 50bp rate cut amid cooling inflation data. Markets rally on dovish expectations.",
            "author": "Bloomberg Markets",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.6,
        },
        {
            "source": "wsj",
            "content": "NVIDIA reports Q4 earnings beat, data center revenue up 400% YoY. Stock surges 8% in after-hours trading.",
            "author": "WSJ Tech",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.8,
        },
        {
            "source": "cnbc",
            "content": "SEC proposes new regulations on cryptocurrency staking services. Industry leaders push back on compliance costs.",
            "author": "CNBC Crypto",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": -0.4,
        },
        {
            "source": "twitter",
            "content": "Just went all in on $TSLA calls. Elon is cooking something big. This is not financial advice but also maybe it is. YOLO",
            "author": "@WSBChad",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.7,
        },
        {
            "source": "reddit",
            "content": "DD: Why the CPI report next week will trigger a massive short squeeze in regional banks. Institutions are overleveraged.",
            "author": "u/DeepValueApe",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.5,
        },
        {
            "source": "twitter",
            "content": "US 10Y yield breaking above 4.5%. This is the trade of the decade. Short bonds, long commodities.",
            "author": "@MacroTrader",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": -0.3,
        },
        {
            "source": "bloomberg",
            "content": "DOJ opens antitrust investigation into major tech company's AI market dominance. Shares drop 5% pre-market.",
            "author": "Bloomberg Law",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": -0.7,
        },
        {
            "source": "reddit",
            "content": "GME is coiling for another squeeze. Short interest back above 20%. The hedgies never learn. Diamond hands.",
            "author": "u/DiamondHandsForever",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.6,
        },
    ]


SAMPLE_SCENARIOS = [
    {
        "name": "Fed Rate Cut Surprise",
        "description": "Federal Reserve announces an emergency 50bp rate cut ahead of schedule",
        "seed_event": "BREAKING: Federal Reserve announces emergency 50 basis point rate cut, citing deteriorating economic conditions. Fed Chair states 'we are prepared to act further if necessary.' US Dollar drops sharply, bond yields plunge.",
        "environment_vars": {
            "market_volatility": "high",
            "sector_focus": "general",
            "election_year": False,
            "fed_stance": "dovish",
        },
    },
    {
        "name": "SEC Crypto Crackdown",
        "description": "SEC announces comprehensive regulations banning crypto staking for retail investors",
        "seed_event": "BREAKING: SEC Commissioner announces sweeping new regulations that would effectively ban cryptocurrency staking services for US retail investors. Major exchanges scramble to comply. Bitcoin drops 12% in minutes.",
        "environment_vars": {
            "market_volatility": "extreme",
            "sector_focus": "crypto",
            "election_year": False,
            "fed_stance": "neutral",
        },
    },
    {
        "name": "NVIDIA Earnings Blowout",
        "description": "NVIDIA reports Q4 earnings 3x above expectations with massive AI demand",
        "seed_event": "BREAKING: NVIDIA reports Q4 earnings of $12.96 EPS vs $5.60 expected. Data center revenue surges 500% YoY to $18.4B. CEO announces next-gen AI chip 'Blackwell Ultra' with 10x performance improvement. Stock gaps up 15% after hours.",
        "environment_vars": {
            "market_volatility": "high",
            "sector_focus": "tech",
            "election_year": False,
            "fed_stance": "neutral",
        },
    },
]
