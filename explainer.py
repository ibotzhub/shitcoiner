"""
Plain-English explanations for every term shown in the UI.
Written for someone who knows nothing about crypto but wants to understand what they're looking at.
Shitcoin-aware — honest about what these signals mean and don't mean.
"""

EXPLAINERS = [
    {
        "term": "Trend score",
        "short": "Our momentum number (0–1). Higher = more action right now.",
        "explanation": (
            "We combine five signals — how much the price spiked today, whether trading volume "
            "is huge relative to the coin's size, whether it's on trending lists, how it's done "
            "over the last week, and how small the coin is — and turn all that into one number. "
            "A high score means this coin is getting a lot of attention right now. "
            "It does NOT mean it will go up. It means people are buying and selling it a lot, "
            "and the price is moving. That's the whole signal."
        ),
    },
    {
        "term": "Vol / MCap ratio",
        "short": "Trading volume ÷ market cap. The best 'something is happening' signal.",
        "explanation": (
            "Imagine a coin's total value is $1 million. If $2 million worth of it traded in one "
            "day, the vol/mcap ratio is 2.0 — twice the entire coin changed hands. That's unusual "
            "and usually means a pump, a listing, big news, or coordinated buying. "
            "For large coins like Bitcoin, this ratio is tiny (0.01–0.05). For a shitcoin "
            "mid-run, you'll see 0.5, 1.0, even higher. It's the single best signal that "
            "something real is moving — but it can also mean a dump is already in progress."
        ),
    },
    {
        "term": "24h %",
        "short": "Price change in the last 24 hours.",
        "explanation": (
            "How much the price moved in one day. +80% means if you had $100 yesterday "
            "it'd be $180 today — on paper. The danger: it can reverse just as fast. "
            "Shitcoins with +100% in 24h are exciting, but they're just as capable of "
            "-80% the next day. This is a momentum signal, not a safe entry point."
        ),
    },
    {
        "term": "7d %",
        "short": "Price change over the last 7 days.",
        "explanation": (
            "Same idea as 24h but zoomed out to a week. A coin up +200% over 7 days and "
            "+30% today might still have room — or it might be exhausted. A coin up +10% "
            "over 7 days but +50% today could be just starting a run. We use both together."
        ),
    },
    {
        "term": "Price",
        "short": "Current price in USD per coin.",
        "explanation": (
            "A coin at $0.000001 is not cheaper or better than one at $50. What matters "
            "is the total market cap and how much it can realistically grow. A low price "
            "just means there are a huge number of coins in circulation. Don't let small "
            "numbers trick you into thinking something is 'affordable'."
        ),
    },
    {
        "term": "Market cap rank",
        "short": "Size ranking vs all other coins. Lower rank # = bigger coin.",
        "explanation": (
            "Rank 1 = Bitcoin (largest). Rank 500 = tiny project. This scanner focuses on "
            "ranks roughly 20–500 — small and micro cap territory. These coins move more, "
            "but they also fail more. Top 20 blue chips (BTC, ETH, etc.) are hidden by "
            "default because they rarely produce the kind of moves this scanner is tracking."
        ),
    },
    {
        "term": "Market cap",
        "short": "Total dollar value of all coins of this type combined.",
        "explanation": (
            "Price × total supply = market cap. A $10M market cap coin needs to 10x to "
            "hit $100M — possible. A $10B coin needs $100B to do the same — much harder. "
            "Smaller market caps can move faster, but they can also go to zero faster."
        ),
    },
    {
        "term": "Volume",
        "short": "Total USD traded in the last 24 hours.",
        "explanation": (
            "How much money actually changed hands today. Low volume means it's hard to "
            "buy or sell without moving the price yourself. Sudden volume spikes (especially "
            "when the vol/mcap ratio gets high) are one of the earliest signals of a move."
        ),
    },
    {
        "term": "Trending bonus",
        "short": "Whether this coin appeared on CoinGecko trending or gainers lists.",
        "explanation": (
            "CoinGecko's trending list is based on what people are searching for. Appearing "
            "there means a lot of people are looking at this coin right now. We also scrape "
            "the gainers page with three browser engines (Chromium, Firefox, Safari) for extra "
            "coverage. A coin on both lists gets a significant score boost."
        ),
    },
    {
        "term": "New / recently listed",
        "short": "Coin that appears to have been listed recently.",
        "explanation": (
            "We flag coins where the all-time low date was within the last 6 months — a rough "
            "proxy for recently listed coins. New listings can move fast but also have no "
            "price history, tiny liquidity, and often no real project behind them. "
            "Highest risk category."
        ),
    },
    {
        "term": "Blue chips (hidden by default)",
        "short": "Top 20 coins by market cap — BTC, ETH, BNB, etc.",
        "explanation": (
            "Big, established coins. Rarely produce the kind of momentum this tool tracks. "
            "Hidden by default to keep the results focused on smaller coins. Toggle them "
            "back in with the 'Include blue chips' switch if you want a full picture."
        ),
    },
]


def get_all() -> list[dict]:
    return list(EXPLAINERS)


def format_for_cli() -> str:
    lines = [
        "",
        "─" * 70,
        "WHAT DOES THIS STUFF MEAN?",
        "─" * 70,
        "",
    ]
    for e in EXPLAINERS:
        lines.append(f"  • {e['term']}")
        lines.append(f"    {e['short']}")
        lines.append(f"    {e['explanation']}")
        lines.append("")
    lines.append(
        "⚠  This is not financial advice. Shitcoins can go to zero. "
        "Only risk money you'd be fine losing entirely."
    )
    lines.append("")
    return "\n".join(lines)
