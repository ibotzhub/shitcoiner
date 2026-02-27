"""Fetch crypto market data from CoinGecko API."""

import time
import requests
from config import COINGECKO_BASE, COINGECKO_TOP_N, REQUEST_TIMEOUT, RATE_LIMIT_WAIT, MAX_RETRIES


class RateLimitError(Exception):
    """Raised when CoinGecko returns 429 — caller should surface this to the user."""


def _get(url: str, params: dict, attempt: int = 0) -> list | dict:
    """GET with retry on transient errors; raises RateLimitError on 429."""
    try:
        r = requests.get(url, params=params, timeout=REQUEST_TIMEOUT)
    except requests.exceptions.Timeout:
        if attempt < MAX_RETRIES:
            time.sleep(2 ** attempt)
            return _get(url, params, attempt + 1)
        raise RuntimeError("CoinGecko timed out — try again in a moment.")
    except requests.exceptions.ConnectionError:
        raise RuntimeError("Can't reach CoinGecko — check your internet connection.")

    if r.status_code == 429:
        raise RateLimitError(
            f"CoinGecko rate limit hit. Wait {RATE_LIMIT_WAIT} seconds and try again. "
            f"(The free API allows ~10-30 requests/minute.)"
        )
    if r.status_code >= 500:
        if attempt < MAX_RETRIES:
            time.sleep(3 * (attempt + 1))
            return _get(url, params, attempt + 1)
        raise RuntimeError(f"CoinGecko server error ({r.status_code}) — try again shortly.")

    r.raise_for_status()
    return r.json()


def _downsample(prices: list[float], n: int = 48) -> list[float]:
    """Reduce a price series to at most n evenly-spaced points for sparklines."""
    if not prices:
        return []
    if len(prices) <= n:
        return prices
    step = len(prices) / n
    return [prices[int(i * step)] for i in range(n)]


def fetch_coins_market(per_page: int = 250, page: int = 1, sparkline: bool = True) -> list[dict]:
    """Fetch market data for coins ordered by market cap descending."""
    url = f"{COINGECKO_BASE}/coins/markets"
    params = {
        "vs_currency": "usd",
        "order": "market_cap_desc",
        "per_page": min(per_page, 250),
        "page": page,
        "sparkline": sparkline,
        "price_change_percentage": "24h,7d",
    }
    return _get(url, params)


def fetch_trending() -> list[dict]:
    """Fetch trending coins from CoinGecko search trends."""
    url = f"{COINGECKO_BASE}/search/trending"
    data = _get(url, {})
    return data.get("coins", [])[:20]


def fetch_simple_prices(ids: list[str]) -> dict[str, dict]:
    """
    Lightweight price fetch for a list of coin IDs.
    Returns {coin_id: {current_price, price_change_percentage_24h, market_cap, total_volume, vol_mcap_ratio}}.
    Used for real-time watchlist polling — much cheaper than a full scan.
    """
    if not ids:
        return {}
    url = f"{COINGECKO_BASE}/simple/price"
    params = {
        "ids": ",".join(ids),
        "vs_currencies": "usd",
        "include_24hr_change": "true",
        "include_market_cap": "true",
        "include_24hr_vol": "true",
    }
    raw = _get(url, params)
    result: dict[str, dict] = {}
    for cid, data in raw.items():
        mcap = data.get("usd_market_cap") or 0
        vol  = data.get("usd_24h_vol") or 0
        result[cid] = {
            "current_price":               data.get("usd"),
            "price_change_percentage_24h": data.get("usd_24h_change"),
            "market_cap":                  mcap,
            "total_volume":                vol,
            "vol_mcap_ratio":              (vol / mcap) if mcap > 0 else 0.0,
        }
    return result


def fetch_gainers_losers() -> tuple[list[dict], list[dict]]:
    """Top gainers and losers by 24h % from the first 100 by market cap."""
    markets = fetch_coins_market(per_page=100, sparkline=False)
    with_pct = [m for m in markets if m.get("price_change_percentage_24h") is not None]
    by_24h   = sorted(with_pct, key=lambda x: x["price_change_percentage_24h"], reverse=True)
    gainers  = by_24h[:15]
    losers   = sorted(by_24h[-15:], key=lambda x: x["price_change_percentage_24h"])
    return gainers, losers


def get_all_market_data(top_n: int | None = None) -> list[dict]:
    """
    Aggregate market data across multiple pages.
    Fetches sparkline (7d hourly prices) and downsamples for charting.
    Pre-computes vol_mcap_ratio for the scorer.
    """
    top_n     = top_n or COINGECKO_TOP_N
    all_coins: list[dict] = []
    page      = 1

    while len(all_coins) < top_n:
        chunk = fetch_coins_market(per_page=250, page=page, sparkline=True)
        if not chunk:
            break
        all_coins.extend(chunk)
        if len(chunk) < 250:
            break
        page += 1

    coins = all_coins[:top_n]

    for c in coins:
        # Extract and downsample sparkline
        sp = c.pop("sparkline_in_7d", None)
        if sp and isinstance(sp.get("price"), list):
            raw = [p for p in sp["price"] if p is not None]
            c["sparkline"] = _downsample(raw)
        else:
            c["sparkline"] = []

        # Pre-compute vol/market-cap ratio
        vol  = c.get("total_volume") or 0
        mcap = c.get("market_cap") or 0
        c["vol_mcap_ratio"] = (vol / mcap) if mcap > 0 else 0.0

    return coins
