from selectolax.parser import HTMLParser
from dataclasses import dataclass
from datetime import date
import sqlite3
from settings import DATABASE, CALENDAR_LIST


@dataclass
class Movie_url:
    name: str
    date: date
    url: str

    def __str__(self):
        return f"{self.date}, {self.name}, {self.url}"


def save(results: list[Movie_url]):
    """Save to database"""
    conn = sqlite3.connect(DATABASE)

    for result in results:
        conn.execute(
            """INSERT INTO movies(name, date, url) VALUES (?,?,?)""",
            (
                result.name,
                result.date.isoformat(),
                result.url,
            ),
        )
    conn.commit()
    conn.close()


def parse(html_page) -> list[Movie_url]:
    """Parse Movie name, date on calendar (usually week), and url portion"""

    DATES = {
        "Jan": 1,
        "Feb": 2,
        "Mar": 3,
        "Apr": 4,
        "May": 5,
        "Jun": 6,
        "Jul": 7,
        "Aug": 8,
        "Sep": 9,
        "Oct": 10,
        "Nov": 11,
        "Dec": 12,
    }

    results = []
    html = HTMLParser(html_page)
    data = html.css(".sc-fb872901-1")

    for d in data:

        date_data = d.css_first("h3.ipc-title__text")
        date_data = date_data.text().replace(",", "").split(" ")
        date_obj = date(
            year=int(date_data[2]), month=DATES.get(date_data[0]), day=int(date_data[1])
        )

        nodes = d.css("a.ipc-metadata-list-summary-item__t")

        for node in nodes:
            # remove (year) and take name from infront of it
            name = node.text().split("(")[0].strip()
            url = node.attributes.get("href", None).replace("?ref_=rlm", "")
            movie = Movie_url(date=date_obj, name=name, url=url)
            results.append(movie)

    return results


with open(CALENDAR_LIST / "movie_urls_2024-12-23.html", "r", encoding="utf-8") as file:
    save(parse(file.read()))
