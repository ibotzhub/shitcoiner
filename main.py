#!/usr/bin/env python3
"""
Crypto Trend Scanner (shitcoin edition) — CLI.
Ranks micro/small-cap coins by momentum. Not financial advice.
"""

import argparse
import sys
from market_data import get_all_market_data, fetch_trending, RateLimitError
from analysis    import rank_coins
from config      import COINGECKO_TOP_N, BROWSER_TYPES


def format_coin(c: dict, rank: int) -> str:
    sym      = c.get("symbol", "").upper()
    name     = (c.get("name") or "")[:18]
    price    = c.get("current_price")
    p24      = c.get("price_change_percentage_24h")
    p7       = c.get("price_change_percentage_7d")
    vmr      = c.get("vol_mcap_ratio")
    score    = c.get("trend_score", 0)
    mc_rank  = c.get("market_cap_rank") or "-"
    new_flag = " [NEW]" if c.get("_newly_listed") else ""

    price_str = f"${price:,.6f}"  if price is not None else "N/A"
    p24_str   = f"{p24:+.2f}%"   if p24  is not None else "N/A"
    p7_str    = f"{p7:+.2f}%"    if p7   is not None else "N/A"
    vmr_str   = f"{vmr:.3f}"     if vmr  is not None else "N/A"

    return (
        f"  {rank:3}. {sym:8} {name:18}{new_flag} "
        f"{price_str:14} 24h:{p24_str:9} 7d:{p7_str:9} "
        f"v/mc:{vmr_str:6} score:{score:.3f} cap#{mc_rank}"
    )


def run_scan(
    top_n: int          = 20,
    fetch: int          | None = None,
    use_browser: bool   = True,
    exclude_blue_chips: bool = True,
) -> list[dict]:
    fetch = fetch or COINGECKO_TOP_N
    warnings: list[str] = []

    market_coins = get_all_market_data(top_n=fetch)

    trending: list[dict] = []
    try:
        trending = fetch_trending()
    except Exception as e:
        warnings.append(f"Warning: trending fetch failed — {e}")

    trend_ids_from_browser: set[str] = set()
    if use_browser:
        try:
            from browser_automation import get_trend_ids_sync
            trend_ids_from_browser = get_trend_ids_sync()
        except ImportError:
            warnings.append("Warning: Playwright not installed — skipping browser automation.")
        except Exception as e:
            warnings.append(f"Warning: browser automation failed — {e}")

    trending_merged = list(trending)
    for cid in trend_ids_from_browser:
        if not any(
            (t.get("item") or t).get("id", "").lower() == cid or
            (t.get("item") or t).get("coin_id", "").lower() == cid
            for t in trending_merged
        ):
            trending_merged.append({"item": {"id": cid, "coin_id": cid}})

    for w in warnings:
        print(w, file=sys.stderr)

    ranked = rank_coins(
        market_coins,
        trending_coins=trending_merged or None,
        exclude_blue_chips=exclude_blue_chips,
    )
    return ranked[:top_n]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Shitcoin momentum scanner — ranks micro/small-cap coins by trend signal. Not financial advice."
    )
    parser.add_argument("-n", "--top",           type=int,  default=20,
                        help="Show top N coins (default 20)")
    parser.add_argument("--fetch",               type=int,  default=COINGECKO_TOP_N,
                        help=f"Fetch N coins from API (default {COINGECKO_TOP_N})")
    parser.add_argument("--no-browser",          action="store_true",
                        help="Skip browser automation (API only)")
    parser.add_argument("--include-blue-chips",  action="store_true",
                        help="Include top-20 blue chips in results (hidden by default)")
    parser.add_argument("--list-browsers",       action="store_true",
                        help="List supported browser types and exit")
    args = parser.parse_args()

    if args.list_browsers:
        print("Supported browser types (Playwright):", ", ".join(BROWSER_TYPES))
        return 0

    print(f"Fetching top {args.fetch} coins from CoinGecko...")
    try:
        top = run_scan(
            top_n=args.top,
            fetch=args.fetch,
            use_browser=not args.no_browser,
            exclude_blue_chips=not args.include_blue_chips,
        )
    except RateLimitError as e:
        print(f"Rate limit: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    print()
    print("=" * 95)
    print("⚠  NOT FINANCIAL ADVICE. Shitcoins are extremely high risk. Scores = momentum only.")
    print("   Blue chips (top 20 by market cap) are hidden. Use --include-blue-chips to show them.")
    print("=" * 95)
    print()
    print(f"Top {len(top)} by shitcoin momentum score  [v/mc = vol/market-cap ratio]")
    print()
    for i, c in enumerate(top, 1):
        print(format_coin(c, i))

    from explainer import format_for_cli
    print(format_for_cli())
    return 0


if __name__ == "__main__":
    sys.exit(main())
