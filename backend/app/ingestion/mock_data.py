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
        {
            "source": "bloomberg",
            "content": "WTI crude surges past $90 as OPEC+ signals deeper production cuts. Energy stocks rally broadly. Inflation concerns resurface.",
            "author": "Bloomberg Commodities",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": -0.3,
        },
        {
            "source": "twitter",
            "content": "Gold breaking $2,400. Central banks can't stop buying. This is the beginning of the end for dollar hegemony. Load up on physical.",
            "author": "@GoldBugMike",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.7,
        },
        {
            "source": "reddit",
            "content": "DD: Silver is the most undervalued commodity on the planet. Industrial demand from solar + EV is about to explode. Gold-to-silver ratio at 85 is historically extreme. $50 silver by EOY.",
            "author": "u/SilverStackerPro",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": 0.8,
        },
        {
            "source": "cnbc",
            "content": "Oil prices could hit $100 if Middle East tensions escalate further, Goldman Sachs warns. Brent crude up 3% today.",
            "author": "CNBC Energy",
            "timestamp": datetime.utcnow().isoformat(),
            "sentiment": -0.4,
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
    {
        "name": "Oil Supply Shock",
        "description": "OPEC+ announces surprise 2M barrel/day production cut amid Middle East tensions",
        "seed_event": "BREAKING: OPEC+ announces emergency 2 million barrel/day production cut effective immediately. Saudi Arabia cites 'market stabilization' but analysts point to escalating Middle East tensions. WTI crude surges 12% to $95/barrel. Airlines and shipping stocks plunge. Gold rallies as safe-haven demand spikes.",
        "environment_vars": {
            "market_volatility": "extreme",
            "sector_focus": "commodities",
            "election_year": False,
            "fed_stance": "neutral",
        },
    },
    {
        "name": "Gold Rush: Dollar Collapse Fear",
        "description": "US credit downgrade triggers flight to gold and silver",
        "seed_event": "BREAKING: Fitch downgrades US sovereign credit rating to AA citing 'fiscal deterioration and debt ceiling brinkmanship.' Gold surges past $2,500/oz, silver jumps 8%. US Dollar Index drops to 2-year low. Treasury yields spike as foreign holders dump US debt. Central banks globally accelerate gold reserves accumulation.",
        "environment_vars": {
            "market_volatility": "extreme",
            "sector_focus": "commodities",
            "election_year": False,
            "fed_stance": "dovish",
        },
    },
    {
        "name": "Silver Squeeze 2.0",
        "description": "Retail investors coordinate a massive silver buying campaign",
        "seed_event": "BREAKING: Reddit's r/WallStreetSilver coordinates largest physical silver buying campaign in history. COMEX silver inventories drop 15% in 48 hours. Silver spikes to $35/oz. Major banks with short positions face margin calls. #SilverSqueeze trends #1 globally. Physical dealers report nationwide shortages.",
        "environment_vars": {
            "market_volatility": "high",
            "sector_focus": "commodities",
            "election_year": False,
            "fed_stance": "neutral",
        },
    },
]
