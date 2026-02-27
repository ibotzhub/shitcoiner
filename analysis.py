"""
Trend and momentum scoring for shitcoin hunting.
Not financial advice — scores measure recent buzz and price action only.
"""

import math
from datetime import datetime, timezone

from config import (
    WEIGHT_PRICE_CHANGE_24H,
    WEIGHT_VOL_MCAP_RATIO,
    WEIGHT_TRENDING,
    WEIGHT_PRICE_CHANGE_7D,
    WEIGHT_MARKET_CAP_RANK,
    NEWLY_LISTED_BONUS,
    BLUE_CHIP_RANK_CUTOFF,
    STABLECOIN_IDS,
    STABLECOIN_SYMBOLS,
)

# Sentinel value returned for coins that are filtered out (stables, blue chips)
FILTERED_OUT = -1.0


def _normalize(value: float, lo: float, hi: float) -> float:
    """Linear clamp+normalize to 0..1."""
    if hi <= lo:
        return 0.5
    return max(0.0, min(1.0, (value - lo) / (hi - lo)))


def _normalize_log(value: float, lo: float, hi: float) -> float:
    """
    Log-scale normalize to 0..1.
    Much better for vol/mcap ratios which span several orders of magnitude.
    """
    if hi <= lo or value <= 0:
        return 0.0
    lv = math.log1p(value)
    ll = math.log1p(max(0.0, lo))
    lh = math.log1p(hi)
    if lh <= ll:
        return 0.5
    return max(0.0, min(1.0, (lv - ll) / (lh - ll)))


def _is_stablecoin(coin: dict) -> bool:
    coin_id  = (coin.get("id") or "").lower()
    symbol   = (coin.get("symbol") or "").lower()
    return coin_id in STABLECOIN_IDS or symbol in STABLECOIN_SYMBOLS


def _is_newly_listed(coin: dict) -> bool:
    """
    Proxy for 'new coin': ATL date within the last 180 days.
    Not perfect but CoinGecko's markets endpoint doesn't give true listing date.
    """
    atl_date = coin.get("atl_date") or ""
    if not atl_date:
        return False
    try:
        dt      = datetime.fromisoformat(atl_date.replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - dt).days
        return age_days <= 180
    except Exception:
        return False


def score_coin(
    coin: dict,
    trend_ids: set[str] | None = None,
    vmr_lo: float = 0.0,
    vmr_hi: float = 1.0,
    pct_24h_lo: float = -50.0,
    pct_24h_hi: float = 200.0,
    pct_7d_lo: float = -50.0,
    pct_7d_hi: float = 400.0,
    exclude_blue_chips: bool = True,
) -> float:
    """
    Compute a shitcoin momentum score (0–1). Returns FILTERED_OUT (-1) for
    stablecoins and blue chips (when exclude_blue_chips=True).
    Higher score = stronger recent momentum. NOT a prediction of future returns.
    """
    trend_ids = trend_ids or set()

    # ── Hard filters ──────────────────────────────────────────────────────────
    if _is_stablecoin(coin):
        return FILTERED_OUT

    rank = coin.get("market_cap_rank")
    if exclude_blue_chips and rank is not None and rank <= BLUE_CHIP_RANK_CUTOFF:
        return FILTERED_OUT

    score = 0.0

    # ── 1. 24h price spike (highest weight, 0.30) ─────────────────────────────
    pct_24 = coin.get("price_change_percentage_24h")
    if pct_24 is not None:
        score += WEIGHT_PRICE_CHANGE_24H * _normalize(pct_24, pct_24h_lo, pct_24h_hi)
    else:
        score += WEIGHT_PRICE_CHANGE_24H * 0.4   # slight penalty for missing data

    # ── 2. Volume / market cap ratio (0.25) ───────────────────────────────────
    # The single best "something is happening relative to the coin's size" signal.
    # Log-scaled because a ratio of 0.5 vs 2.0 matters, but 2.0 vs 5.0 matters less.
    vmr = coin.get("vol_mcap_ratio", 0.0)
    score += WEIGHT_VOL_MCAP_RATIO * _normalize_log(vmr, vmr_lo, vmr_hi)

    # ── 3. Trending / gainers list bonus (0.20) ───────────────────────────────
    cid = (coin.get("id") or "").lower()
    if cid in trend_ids:
        score += WEIGHT_TRENDING * 1.0   # on the list: full weight
    else:
        score += WEIGHT_TRENDING * 0.05  # off the list: tiny baseline (not zero)

    # ── 4. 7d price change — sustained run (0.15) ─────────────────────────────
    pct_7 = coin.get("price_change_percentage_7d")
    if pct_7 is not None:
        score += WEIGHT_PRICE_CHANGE_7D * _normalize(pct_7, pct_7d_lo, pct_7d_hi)
    else:
        score += WEIGHT_PRICE_CHANGE_7D * 0.4

    # ── 5. Market cap rank — prefer micro/small cap (0.10) ───────────────────
    # Rank 50 = moderate, 500 = tiny. Both can move. We want the sweet spot, not rank 1.
    if rank is not None:
        cutoff = BLUE_CHIP_RANK_CUTOFF if exclude_blue_chips else 1
        rank_score = _normalize(rank, cutoff, 500)
        score += WEIGHT_MARKET_CAP_RANK * rank_score
    else:
        score += WEIGHT_MARKET_CAP_RANK * 0.7  # unknown rank → treat as small cap

    # ── 6. Newly listed proxy bonus (+0.05 flat) ──────────────────────────────
    if _is_newly_listed(coin):
        score += NEWLY_LISTED_BONUS

    return min(1.0, max(0.0, score))


def rank_coins(
    market_coins: list[dict],
    trending_coins: list[dict] | None = None,
    exclude_blue_chips: bool = True,
) -> list[dict]:
    """
    Score every coin, filter out stables and (optionally) blue chips,
    then return sorted list with 'trend_score' and 'rank' attached.
    """
    # Build trending ID set
    trend_ids: set[str] = set()
    if trending_coins:
        for t in trending_coins:
            item = t.get("item") if isinstance(t.get("item"), dict) else t
            if item:
                tid = (item.get("id") or item.get("coin_id") or "").lower()
                if tid:
                    trend_ids.add(tid)

    # Range stats — computed only on non-filtered coins for fair normalization
    non_stable = [c for c in market_coins if not _is_stablecoin(c)]

    vmrs    = [c.get("vol_mcap_ratio", 0.0) for c in non_stable]
    pct_24s = [c.get("price_change_percentage_24h") for c in non_stable if c.get("price_change_percentage_24h") is not None]
    pct_7s  = [c.get("price_change_percentage_7d") for c in non_stable  if c.get("price_change_percentage_7d")  is not None]

    vmr_lo,    vmr_hi    = (min(vmrs),    max(vmrs))    if vmrs    else (0.0, 1.0)
    pct_24h_lo, pct_24h_hi = (min(pct_24s), max(pct_24s)) if pct_24s else (-50.0, 200.0)
    pct_7d_lo,  pct_7d_hi  = (min(pct_7s),  max(pct_7s))  if pct_7s  else (-50.0, 400.0)

    # Score each coin
    scored: list[dict] = []
    for c in market_coins:
        s = score_coin(
            c,
            trend_ids=trend_ids,
            vmr_lo=vmr_lo,
            vmr_hi=vmr_hi,
            pct_24h_lo=pct_24h_lo,
            pct_24h_hi=pct_24h_hi,
            pct_7d_lo=pct_7d_lo,
            pct_7d_hi=pct_7d_hi,
            exclude_blue_chips=exclude_blue_chips,
        )
        if s == FILTERED_OUT:
            continue
        c["trend_score"] = s
        scored.append(c)

    ranked = sorted(scored, key=lambda x: x["trend_score"], reverse=True)
    for i, c in enumerate(ranked, 1):
        c["rank"] = i

    return ranked
