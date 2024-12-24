from playwright.sync_api import sync_playwright
from playwright_stealth import stealth_sync
from datetime import datetime

from settings import CALENDAR_LIST


def scrape(url):
    """Scrape movie urls off calendar and save in a file with today's date."""
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        stealth_sync(page)
        page.goto(url)

        timestamp = datetime.now().date()

        with open(
            CALENDAR_LIST / f"movie_urls_{timestamp}.html",
            "w",
            encoding="utf-8",
        ) as file:
            file.write(page.content())

        browser.close()


url = "https://www.imdb.com/calendar/?region=GB&type=MOVIE&ref_=rlm"

scrape(url)
# https://www.imdb.com/calendar/?region=US&type=MOVIE&ref_=rlm
# https://www.imdb.com/calendar/?region=GB&type=TV_EPISODE&ref_=rlm
