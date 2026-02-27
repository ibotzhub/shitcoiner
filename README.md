# SHITCOINER

native desktop momentum scanner for people who actually shitcoin

---

okay so basically i got tired of having 47 tabs open trying to figure out which coins were actually moving vs which ones were just sitting there doing nothing so i built this

it pulls live data from coingecko, scores every coin by how hard its actually moving right now, and gives you a ranked list. stablecoins and blue chips filtered out by default because we dont care about those. top 500 coins by market cap, focused on the micro and small cap stuff where the actual action is

---

## what it does

- **ranks coins by momentum** - 24h price spike, volume vs market cap ratio, trending lists, 7 day run, how small the coin is. all combined into one score
- **vol/mcap ratio** is the big one - if a tiny coin is doing huge volume relative to its size something is happening. thats usually the earliest signal
- **sparklines** - little 7 day chart next to every coin so you can see at a glance if its a breakout or a dead cat
- **signal badges** - strong momentum / volume spike watch / fading / accumulation
- **my bag** - star any coin, optionally put in your entry price and how many you bought, tracks your P&L live and updates every 10 seconds. you can literally just leave it open and watch stuff move in real time
- **alerts** - set a price or score threshold and get a desktop notification when it hits
- **ai take** - if you have an openai or anthropic key it'll give you a plain english read on the scan. doesnt tell you to buy anything just explains whats interesting

---

## install

you need python 3.10+

```bash
pip install requests PyQt6 python-dotenv
python app.py
```

thats it. window opens. no browser, no localhost, no flask, nothing weird

---

## build a standalone exe

if you want to send it to someone who doesnt have python:

```bash
./build_standalone.sh
```

- macOS → `dist/SHITCOINER.app`
- Windows → `dist/SHITCOINER.exe`
- Linux → `dist/SHITCOINER`

double click and it just works

---

## ai commentary

settings → ai commentary tab → paste your openai or anthropic key → save

then run a scan and hit ai take. it reads the results and tells you whats sus in plain english. doesnt give financial advice just explains whats moving and why it might be interesting

---

## the files

```
app.py                ← the whole desktop app
config.py             ← scoring weights, stablecoin list, settings
analysis.py           ← the scoring engine
market_data.py        ← coingecko api calls
ai_commentary.py      ← openai / anthropic integration
explainer.py          ← term definitions
browser_automation.py ← playwright scraper for extra trending signal (optional)
requirements.txt      ← dependencies
build_standalone.sh   ← builds the executable
```

---

## disclaimer

not financial advice. i put warnings everywhere. shitcoins are extremely high risk and can go to zero overnight or faster. this tool shows momentum signals only, thats it. whether you decide to put money in something is entirely on you - i built this for research /cough and i am not responsible for your financial decisions. you were warned, multiple times, in multiple places. its your call not mine

tbh i cant even afford to use this app so if u really secure the bag with this hmu alms for the broke bitch

---

## license

use it however you want. no warranty. dont blame me
