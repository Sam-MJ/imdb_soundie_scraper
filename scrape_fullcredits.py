from curl_cffi import requests
from datetime import datetime
from pathlib import Path
import re
import sqlite3

from settings import DATABASE, FULLCREDITS


def scrape(name: str, url: str) -> None:

    r = requests.get(f"https://www.imdb.com{url}fullcredits/", impersonate="chrome")

    # Create a folder with today's date
    timestamp = datetime.now().date()
    Path(FULLCREDITS / f"{timestamp}/").mkdir(parents=False, exist_ok=True)

    # write page contents into html file with file system compatible name
    with open(
        FULLCREDITS / f"{timestamp}/{clean_name(name)}.html",
        "w",
        encoding="utf-8",
    ) as file:
        file.write(r.text)


def clean_name(name: str) -> str:
    """Force only digits and characters"""
    clean_name = re.findall("[A-Za-z0-9]", name)
    return "".join(clean_name)


def fetch_urls() -> list[list[str, str]]:
    """get urls from database"""
    conn = sqlite3.connect(DATABASE)
    cur = conn.cursor()

    cur.execute("SELECT name, url FROM movies;")
    rows = cur.fetchall()
    conn.close()

    return rows


if __name__ == "__main__":
    rows = fetch_urls()
    for row in rows:
        scrape(row[0], row[1])
