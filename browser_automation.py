"""Browser automation: run in multiple browser engines and scrape trend/gainer pages."""

import asyncio
import re
from config import BROWSER_TYPES, TREND_URLS


def _extract_trending_ids(html: str) -> set[str]:
    """Extract coin ids from CoinGecko trending/gainers HTML (links like /en/coins/bitcoin)."""
    ids = set()
    for m in re.finditer(r"/en/coins/([a-z0-9_-]+)", html, re.I):
        ids.add(m.group(1).lower())
    return ids


async def scrape_with_browser(browser_type: str, url: str) -> str:
    """Launch one browser type, navigate to url, return page HTML."""
    from playwright.async_api import async_playwright

    html = ""
    async with async_playwright() as p:
        try:
            if browser_type == "chromium":
                browser = await p.chromium.launch(headless=True)
            elif browser_type == "firefox":
                browser = await p.firefox.launch(headless=True)
            else:
                browser = await p.webkit.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="domcontentloaded", timeout=20000)
            await page.wait_for_timeout(2000)
            html = await page.content()
            await browser.close()
        except Exception as e:
            print(f"  [{browser_type}] {url}: {e}")
    return html


async def gather_trend_ids_from_browsers() -> set[str]:
    """Run all configured browsers, hit trend URLs, merge scraped coin ids."""
    all_ids = set()
    for url in TREND_URLS:
        for b in BROWSER_TYPES:
            try:
                html = await scrape_with_browser(b, url)
                all_ids |= _extract_trending_ids(html)
            except Exception as e:
                print(f"  Skip {b} / {url}: {e}")
    return all_ids


def get_trend_ids_sync() -> set[str]:
    """Synchronous wrapper for gather_trend_ids_from_browsers."""
    return asyncio.run(gather_trend_ids_from_browsers())


async def run_all_browsers_demo():
    """Launch each browser type once to show they're available (optional demo)."""
    from playwright.async_api import async_playwright

    async with async_playwright() as p:
        for name in BROWSER_TYPES:
            try:
                if name == "chromium":
                    b = await p.chromium.launch(headless=True)
                elif name == "firefox":
                    b = await p.firefox.launch(headless=True)
                else:
                    b = await p.webkit.launch(headless=True)
                page = await b.new_page()
                await page.goto("https://www.coingecko.com/en/trending", timeout=15000)
                await page.wait_for_timeout(1500)
                ids = _extract_trending_ids(await page.content())
                await b.close()
                print(f"  {name}: found {len(ids)} trend ids")
            except Exception as e:
                print(f"  {name}: not available - {e}")
