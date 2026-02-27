"""
Optional AI commentary on shitcoin scan results.
Uses OpenAI or Anthropic (set OPENAI_API_KEY or ANTHROPIC_API_KEY in .env or Settings).
Not financial advice.
"""

import os


def _build_prompt(coins_summary: str) -> str:
    return f"""You are a no-nonsense crypto analyst who understands small-cap and micro-cap coins ("shitcoins"). Below is a ranked list of coins from a momentum scanner that specifically targets coins ranked outside the top 20 by market cap — micro-cap, small-cap, newly listed, or unusually high trading volume relative to their size.

Write 3–4 short paragraphs in plain English that:
1) Summarize what stands out — which coins have the strongest 24h momentum, unusual volume/market cap ratios (means something's pumping relative to the coin's size), or showed up on trending lists.
2) Briefly explain what "vol/mcap ratio" means in plain English (if it's high, trading volume was huge compared to the coin's total value — a key signal that something is happening).
3) Remind the reader, clearly but without lecturing: this is speculative momentum data, not a buy signal. Shitcoins can move +500% or go to zero in the same week. Only risk money you'd be fine losing entirely.
4) Do NOT give price targets. Do NOT recommend buying or selling specific coins.

Keep it real and direct — like advice from a friend who's been in the trenches, not a corporate disclaimer.

Scan results (ranked by shitcoin momentum score):
{coins_summary}
"""


def _safe_error(e: Exception) -> str:
    """Return a user-friendly error string without leaking SDK internals."""
    msg = str(e)
    # Strip verbose request details that SDKs sometimes include
    if len(msg) > 200:
        msg = msg[:200] + "…"
    # Map common error types to plain messages
    t = type(e).__name__
    if "AuthenticationError" in t or "401" in msg:
        return "API key invalid or expired — check your key in Settings."
    if "RateLimitError" in t or "429" in msg:
        return "AI provider rate limited — wait a minute and try again."
    if "Connection" in t or "Timeout" in t:
        return "Can't reach the AI provider — check your internet connection."
    return f"AI error: {t}"


def get_ai_commentary(coins: list[dict]) -> tuple[str | None, str | None]:
    """
    Returns (commentary_text, None) on success or (None, error_message) on failure.
    Tries OpenAI first, then Anthropic.
    """
    if not coins:
        return None, "Run a scan first so the AI has data to comment on."

    lines = []
    for c in coins[:25]:
        sym        = (c.get("symbol") or "").upper()
        name       = (c.get("name") or "")[:30]
        price      = c.get("current_price")
        p24        = c.get("price_change_percentage_24h")
        vmr        = c.get("vol_mcap_ratio")
        score      = c.get("trend_score")
        mc_rank    = c.get("market_cap_rank")
        new_flag   = " [NEW]" if c.get("newly_listed") else ""

        price_str  = f"${price:,.6f}" if price is not None else "N/A"
        p24_str    = f"{p24:+.2f}%"   if p24  is not None else "N/A"
        vmr_str    = f"{vmr:.3f}"     if vmr  is not None else "N/A"
        score_str  = f"{score:.3f}"   if score is not None else "—"
        rank_str   = f"#{mc_rank}"    if mc_rank           else "unranked"

        lines.append(
            f"  {sym} ({name}){new_flag} cap_rank={rank_str} price={price_str} "
            f"24h={p24_str} vol/mcap={vmr_str} score={score_str}"
        )

    summary = "\n".join(lines)
    prompt  = _build_prompt(summary)

    # ── Try OpenAI ────────────────────────────────────────────────────────────
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if api_key:
        try:
            from openai import OpenAI
            client = OpenAI(api_key=api_key)
            r      = client.chat.completions.create(
                model=os.getenv("OPENAI_MODEL", "gpt-4o-mini"),
                messages=[
                    {"role": "system", "content": "You are a direct, clear analyst. Never give buy/sell advice. Always note crypto risk. Explain things simply."},
                    {"role": "user",   "content": prompt},
                ],
                temperature=0.5,
                max_tokens=700,
            )
            text = r.choices[0].message.content
            return (text.strip(), None) if text else (None, "AI returned no text.")
        except ImportError:
            return None, "OpenAI SDK not installed — run: pip install openai"
        except Exception as e:
            return None, _safe_error(e)

    # ── Try Anthropic ─────────────────────────────────────────────────────────
    api_key = os.getenv("ANTHROPIC_API_KEY", "").strip()
    if api_key:
        try:
            from anthropic import Anthropic
            client = Anthropic(api_key=api_key)
            r      = client.messages.create(
                model=os.getenv("ANTHROPIC_MODEL", "claude-haiku-4-5-20251001"),
                max_tokens=700,
                system="You are a direct, clear analyst. Never give buy/sell advice. Always note crypto risk. Explain things simply.",
                messages=[{"role": "user", "content": prompt}],
            )
            text = r.content[0].text if r.content else ""
            return (text.strip(), None) if text else (None, "AI returned no text.")
        except ImportError:
            return None, "Anthropic SDK not installed — run: pip install anthropic"
        except Exception as e:
            return None, _safe_error(e)

    return None, "Add OPENAI_API_KEY or ANTHROPIC_API_KEY in Settings to enable AI commentary."


def is_ai_configured() -> bool:
    return (
        bool(os.getenv("OPENAI_API_KEY", "").strip()) or
        bool(os.getenv("ANTHROPIC_API_KEY", "").strip())
    )
