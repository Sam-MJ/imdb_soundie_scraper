from pathlib import Path
from selectolax.parser import HTMLParser
import sqlite3
import re

from settings import DATABASE, FULLCREDITS


def parse_movie_name(html_page):
    """Return movie name, this is so that it can be used to populate the junction table"""
    html = HTMLParser(html_page)
    data = html.css_first("h3 a")

    return data.text()


def parse(html_page):
    """Parse the sound department from the full credits list"""
    results = []

    html = HTMLParser(html_page)
    data = html.css_first("h4#sound_department")

    # Find the next sibling 'table'
    if not data:
        return

    sound_crew = data.next

    # Find the next sibling 'table'
    while sound_crew and sound_crew.tag != "table":
        sound_crew = sound_crew.next

    # Extract the data from the table
    sound_crew_table = sound_crew.css_first("tbody")
    members = sound_crew_table.css("tr")

    # Extract name and role from the text string
    for member in members:
        m = member.text(strip=True).split("...")
        results.append((m[0], m[1]))

    return results


def clean(results: list[tuple[str, str]]):
    """Remove unwanted and duplicate roles from the results list"""
    BLACKLIST = {
        "turkey",
        "uk",
        "80 hertz studios",
        "abu dhabi",
        "atlanta",
        "cas",
        "dailies",
        "daily",
        "disney",
        "e2",
        "formosa at paramount",
        "fox studio lot",
        "goldcrest post production",
        "ii° unit",
        "kradr",
        "la unit",
        "los angeles",
        "malaysia unit",
        "malta",
        "molinare",
        "mpse",
        "new york",
        "new zealand",
        "nickelodeon animation studios",
        "norway",
        "ny unit",
        "pacific standard sound",
        "skywalker sound",
        "smart post sound",
        "soundbyte studios",
        "soundtrack new york",
        "spectrum films",
        "splinter unit",
        "splinter unit dailies",
        "warner bros",
    }

    clean_results = set()

    for result in results:
        role = result[1].lower()

        # Remove . - or anything between brackets
        role = re.sub(r"[\.\-]|\(.*\)", "", role)
        role = role.replace("re recording", "rerecording")
        # Split any roles that have / : & or 'and'
        role = re.split(r"[/:&]|\b(?:and)\b", role)
        # if re.split is used, this creates a list
        if isinstance(role, list):
            for r in role:
                r = r.strip()
                if r not in BLACKLIST:
                    clean_results.add((result[0], r))
        else:
            role = role.strip()
            if role not in BLACKLIST:
                clean_results.add((result[0], role))

    return clean_results


def save(clean_results: list[tuple], movie_name: str):
    """Save results to database"""

    conn = sqlite3.connect(DATABASE)

    for result in clean_results:
        soundie_name = result[0]
        role_name = result[1]
        conn.execute("INSERT OR IGNORE INTO soundies(name) VALUES (?)", (soundie_name,))
        conn.execute("INSERT OR IGNORE INTO roles(name) VALUES (?)", (role_name,))
        conn.execute(
            """INSERT OR IGNORE INTO soundie_movie (soundie_id, movie_id)
            SELECT soundie_id, movie_id
            FROM soundies s, movies m
            WHERE s.name = ? AND m.name = ?;""",
            (soundie_name, movie_name),
        )
        conn.execute(
            """INSERT OR IGNORE INTO soundie_role (soundie_id, role_id)
            SELECT soundie_id, role_id
            FROM soundies s, roles r
            WHERE s.name = ? AND r.name = ?""",
            (soundie_name, role_name),
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":

    files = Path(FULLCREDITS / "2024-12-23").glob("*")

    for file in files:
        with open(file, "r", encoding="utf-8") as f:
            data = f.read()

            movie_name = parse_movie_name(data)
            parsed_results = parse(data)

            if parsed_results:
                save(clean(parsed_results), movie_name)
