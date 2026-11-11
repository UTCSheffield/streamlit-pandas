"""Build the NBA yearly honours table (champions of each competition) from Wikipedia.

Run `python nba_honours.py` (needs internet access) to refresh nba_honours.json.
"""

import json
from pathlib import Path
import re
from urllib.parse import quote


HONOURS_FILE = Path(__file__).with_name("nba_honours.json")
HONOURS_HEADERS = [
    "Season", "NBA Champion", "NBA Finals Runner-up",
    "Eastern Conference Champion", "Western Conference Champion", "NBA Cup Champion",
]
NOT_HELD = "Not held"
WIKI_URL = "https://en.wikipedia.org/w/api.php?action=parse&prop=wikitext&format=json&formatversion=2&page={}"
CONFERENCE_ROW = re.compile(r"^\|\s*\{\{nbay\|(\d{4})\}\}\s*\|\|(.*)$", re.MULTILINE)


def season_label(start_year):
    return f"{start_year}-{(start_year + 1) % 100:02d}"


def wikitext(page):
    from create_nba_workbooks import get_json  # imported late: that module imports this one

    return get_json(WIKI_URL.format(quote(page)))["parse"]["wikitext"]


def team_name(cell):
    link = re.search(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", cell)
    return (link.group(2) or link.group(1)).strip()


def conference_champions(conference):
    """Return {start_year: (team, won_finals)} for one conference."""
    champions = {}
    for match in CONFERENCE_ROW.finditer(wikitext(f"{conference}_Conference_(NBA)")):
        cells = match.group(2).split("||")
        if len(cells) < 3 or "NBA Finals" not in cells[2]:
            continue
        champions[int(match.group(1))] = (team_name(cells[0]), "Won" in cells[2])
    return champions


def cup_champions():
    """Return {start_year: team} from the NBA Cup 'Results by team' table."""
    text = wikitext("NBA_Cup")
    text = text[text.index("Results by team"):]
    champions = {}
    for row in text.split("\n|-")[1:]:
        cells = row.split("||")
        if len(cells) < 6 or "[[" not in cells[0]:
            continue
        for year in re.findall(r"\|(\d{4})\]\]", cells[-2]):
            champions[int(year)] = team_name(cells[0])
    return champions


def build_honours():
    east = conference_champions("Eastern")
    west = conference_champions("Western")
    cup = cup_champions()
    rows = []
    for year in sorted(set(east) & set(west)):
        east_team, east_won = east[year]
        west_team, west_won = west[year]
        if east_won == west_won:
            raise ValueError(f"Inconsistent Finals result for {season_label(year)}")
        champion, runner_up = (east_team, west_team) if east_won else (west_team, east_team)
        rows.append([
            season_label(year), champion, runner_up, east_team, west_team,
            cup.get(year, NOT_HELD),
        ])
    return rows


def load_honours():
    return json.loads(HONOURS_FILE.read_text(encoding="utf-8"))


if __name__ == "__main__":
    honours = build_honours()
    HONOURS_FILE.write_text(json.dumps(honours, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Wrote {len(honours)} seasons to {HONOURS_FILE}")
