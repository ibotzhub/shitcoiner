# HOW TO USE SHITCOINER

> ⚠ This is not financial advice. Shitcoins are extremely high risk.
> Scores show momentum only. Never invest more than you can afford to lose entirely.

---

## The basics

When you open the app you'll see the main window with a toolbar at the top
and an empty results table. Hit **▶ RUN SCAN** to pull live data from CoinGecko
and rank coins by momentum.

---

## Running a scan

1. Set **TOP** — how many coins to show in the results (default 25)
2. Set **FETCH** — how many coins to pull from CoinGecko before scoring
   - TOP 300 = faster, mid-cap focus
   - TOP 500 = more coins, deeper into micro-cap territory (recommended)
3. Check **INCLUDE BLUE CHIPS** if you want BTC/ETH/top 20 in the results
   (they're hidden by default — they rarely produce the moves this tool tracks)
4. Hit **▶ RUN SCAN**

The scan takes 10–30 seconds depending on your internet. It fetches prices,
volume, 7-day sparklines, and trending data, then scores everything.

---

## Reading the results

| Column | What it means |
|--------|--------------|
| # | Rank — #1 has the strongest momentum right now |
| 7D CHART | Sparkline of the last 7 days. Green = up, red = down |
| PRICE | Current price in USD |
| 24H % | How much the price moved in the last 24 hours |
| V/MCAP | **Volume ÷ Market Cap** — the key shitcoin signal. A ratio of 0.5+ means trading volume is huge relative to the coin's size. Something is happening. |
| SIGNAL | Momentum signal based on score + velocity + volume |
| SCORE | Combined momentum score from 0 to 1. Higher = more action |
| CAP # | Market cap rank — smaller number = bigger coin |

---

## Signals explained

| Signal | What it means |
|--------|--------------|
| ● STRONG MOMENTUM | Score is high and rising. Most active signal. |
| ● VOL SPIKE | Big volume relative to coin size. Something's moving. |
| ● FADING | Score is low and dropping. Momentum drying up. |
| ◐ ACCUMULATION? | High volume but score not yet spiking. Watch it. |
| ○ LOW SIGNAL | Not much happening right now. |

**None of these are buy or sell instructions.** They are momentum readings only.

---

## My Bag — watchlist and portfolio tracking

Click the **☆** star next to any coin to add it to your bag.

A dialog opens where you can (all optional):
- Enter your **entry price** and **number of coins** to track P&L
- Set a **price alert** — notifies you if price drops below this
- Set a **score alert** — notifies you if momentum drops below this

Your bag appears at the top of the window and **updates every 10 seconds**
with fresh prices. P&L shows in green (profit) or red (loss).

To remove a coin from your bag, click **✕** next to it.

Your bag is saved automatically and persists between sessions.

---

## Alerts and notifications

When a coin in your bag hits a price or score alert, you'll get a system
notification (the kind that pops up in the corner of your screen).

Make sure your OS has notifications enabled for the app if you want these.

---

## AI commentary

If you have an OpenAI or Anthropic API key:

1. Click **⚙ SETTINGS** → **AI COMMENTARY** tab
2. Paste your key → **SAVE KEYS**
3. Run a scan
4. Click **🤖 AI TAKE**

The AI gives you a plain-English read on what the scan found — which coins
have unusual volume, what the top of the list has in common, and a reminder
that all of this is speculation. It will not tell you to buy or sell anything.

---

## Settings

**⚙ SETTINGS** in the top right:

- **AI COMMENTARY tab** — add OpenAI or Anthropic key for AI analysis
- **EXCHANGE tab** — Binance key (for future features only, the app does NOT trade)

Keys are stored locally in `~/.shitcoiner/.env` — they never leave your machine
except to go directly to OpenAI or Anthropic when you click AI TAKE.

---

## Tips for actually using this

- **V/MCAP is the most important column.** A coin with a ratio above 0.3–0.5
  is seeing unusual trading activity relative to its size. That's early signal.

- **Run the scan multiple times.** The score velocity arrows (▲▼) show whether
  momentum is building or fading between scans. A coin jumping from 0.5 to 0.8
  across two scans is more interesting than one sitting at 0.8 both times.

- **Star anything interesting immediately.** The 10-second price polling in
  your bag will track it for you while you research.

- **Small V/MCAP + high 24h% = possible fake pump.** Big V/MCAP + moderate
  24h% = organic accumulation. The combination matters more than either alone.

- **The app fetches from CoinGecko's free API.** If you see a rate limit warning,
  wait 60 seconds and scan again. Don't run scans back to back constantly.

---

## What this tool cannot do

- It cannot predict the future
- It cannot tell you when to buy or sell
- It cannot guarantee any coin goes up
- It does not have access to your exchange or wallet
- It does not place trades

Shitcoins can go to zero. Use this as a research starting point, not a
decision-making system. Always do your own research.
