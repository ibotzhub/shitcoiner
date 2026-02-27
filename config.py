"""Configuration and constants — shitcoin momentum scanner."""

# ── CoinGecko API ─────────────────────────────────────────────────────────────
COINGECKO_BASE   = "https://api.coingecko.com/api/v3"
COINGECKO_TOP_N  = 500   # fetch top 500 by market cap — small/micro cap territory
REQUEST_TIMEOUT  = 15
RATE_LIMIT_WAIT  = 65    # seconds to wait after a 429 before telling the user to retry
MAX_RETRIES      = 2     # number of retry attempts on transient errors

# ── Browser automation ────────────────────────────────────────────────────────
BROWSER_TYPES = ["chromium", "firefox", "webkit"]
TREND_URLS = [
    "https://www.coingecko.com/en/trending",
    "https://www.coingecko.com/en/gainers",
]

# ── Scoring weights (must sum to 1.00) ────────────────────────────────────────
# These are tuned for shitcoin momentum hunting, not blue-chip tracking.
WEIGHT_PRICE_CHANGE_24H = 0.30   # short burst spike — biggest signal
WEIGHT_VOL_MCAP_RATIO   = 0.25   # volume / market cap: "something's happening relative to size"
WEIGHT_TRENDING         = 0.20   # CoinGecko trending / browser-scraped gainers bonus
WEIGHT_PRICE_CHANGE_7D  = 0.15   # sustained run over a week
WEIGHT_MARKET_CAP_RANK  = 0.10   # prefer rank 50–500 (micro/small cap volatility zone)
# ──────────────────────────────────────────────────────────────────────────────
# WEIGHT_TOTAL = 1.00
# Newly listed proxy: flat additive bonus on top, clamped to 1.0
NEWLY_LISTED_BONUS      = 0.05   # added if atl_date is within ~180 days (new coin heuristic)

# ── Blue chip exclusion ───────────────────────────────────────────────────────
# Coins ranked ≤ this by market cap are considered "blue chips" and hidden by default.
# User can toggle them back in via the UI.
BLUE_CHIP_RANK_CUTOFF = 20

# ── Stablecoin exclusion ──────────────────────────────────────────────────────
# Always excluded — they'll never spike and just pollute the results.
STABLECOIN_IDS: set[str] = {
    "tether", "usd-coin", "binance-usd", "dai", "true-usd", "pax-dollar",
    "frax", "usdd", "neutrino", "gemini-dollar", "liquity-usd", "fei-usd",
    "flex-usd", "celo-dollar", "terrausd", "terra-usd", "usdp", "nusd",
    "usdk", "usdx", "dola-usd", "bean", "euro-coin", "first-digital-usd",
    "paypal-usd", "usde", "ethena-usde", "mountain-protocol-usdm",
    "usual-usd", "resolv-usr", "sky-usds",
}
STABLECOIN_SYMBOLS: set[str] = {
    "usdt", "usdc", "busd", "dai", "tusd", "usdp", "usdd", "frax",
    "lusd", "susd", "gusd", "cusd", "eurc", "pyusd", "fdusd", "usde",
    "usds", "usdm", "usr", "usd+", "usd0", "crvusd", "mkusd",
}
