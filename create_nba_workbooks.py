"""Create matching Excel workbooks using ESPN NBA regular-season statistics."""

import argparse
from datetime import datetime, timezone
import json
from pathlib import Path
from urllib.request import Request, urlopen

from openpyxl import Workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


PLAYERS = {
    "LeBron James": 1966,
    "Stephen Curry": 3975,
    "Luka Doncic": 3945274,
    "Nikola Jokic": 3112335,
    "Giannis Antetokounmpo": 3032977,
    "Shai Gilgeous-Alexander": 4278073,
    "Jayson Tatum": 4065648,
    "Kevin Durant": 3202,
    "Victor Wembanyama": 5104157,
    "LaMelo Ball": 4432816,
}
LEGENDS = {"Michael Jordan": 1035, "Kobe Bryant": 110}
HEADERS = [
    "Season", "Player", "Team", "Games", "Points", "Rebounds",
    "Assists", "Steals", "Blocks", "3-Pointers Made",
]
STATS_URL = "https://site.web.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{}/stats"
PROFILE_URL = "https://site.api.espn.com/apis/common/v3/sports/basketball/nba/athletes/{}"
OUTPUT = Path(__file__).parent / "nba_workbooks"


def get_json(url):
    request = Request(url, headers={"User-Agent": "NBA classroom workbook generator"})
    with urlopen(request, timeout=30) as response:
        return json.load(response)


def load_player(name, player_id, active):
    profile = get_json(PROFILE_URL.format(player_id))["athlete"]
    if profile["displayName"] != name or (active and not profile["active"]):
        raise ValueError(f"Unexpected profile or inactive player: {name}")
    data = get_json(STATS_URL.format(player_id))
    categories = {category["name"]: category for category in data["categories"]}
    averages = categories["averages"]
    totals = categories["totals"]
    games_index = averages["names"].index("gamesPlayed")
    games = {
        (row["season"]["year"], row.get("teamId")): int(row["stats"][games_index])
        for row in averages["statistics"] if row.get("teamId")
    }
    team_names = {str(team["id"]): team["displayName"] for team in data["teams"].values()}
    indices = {stat: totals["names"].index(stat) for stat in (
        "points", "totalRebounds", "assists", "steals", "blocks",
        "threePointFieldGoalsMade-threePointFieldGoalsAttempted",
    )}
    rows = []
    for row in totals["statistics"]:
        team_id = row.get("teamId")
        if not team_id:
            continue
        stats = row["stats"]
        three_pointers = stats[indices["threePointFieldGoalsMade-threePointFieldGoalsAttempted"]]
        rows.append([
            row["season"]["displayName"], name, team_names[str(team_id)],
            games[(row["season"]["year"], team_id)],
            int(stats[indices["points"]]), int(stats[indices["totalRebounds"]]),
            int(stats[indices["assists"]]), int(stats[indices["steals"]]),
            int(stats[indices["blocks"]]), int(three_pointers.split("-")[0]),
        ])
    if not rows:
        raise ValueError(f"No regular-season data for {name}")
    return rows


def add_table(sheet, headers, rows):
    sheet.append(headers)
    for row in rows:
        sheet.append(row)
    sheet.freeze_panes = "A2"
    sheet.auto_filter.ref = sheet.dimensions
    for cell in sheet[1]:
        cell.fill = PatternFill("solid", fgColor="173C4B")
        cell.font = Font(bold=True, color="FFFFFF")
    for column in sheet.columns:
        width = min(32, max(12, max(len(str(cell.value or "")) for cell in column) + 2))
        sheet.column_dimensions[get_column_letter(column[0].column)].width = width


def make_workbook(player_id, player_rows, retrieved):
    workbook = Workbook()
    workbook.properties.description = f"ESPN regular-season statistics, retrieved {retrieved}. {STATS_URL.format(player_id)}"
    seasons = workbook.active
    seasons.title = "Seasons"
    add_table(seasons, HEADERS, player_rows)
    return workbook


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    all_players = {**PLAYERS, **LEGENDS}
    parser.add_argument("--player", choices=all_players, help="Create just one player's workbook")
    args = parser.parse_args()
    selected = {args.player: all_players[args.player]} if args.player else all_players
    player_data = {
        name: load_player(name, player_id, name in PLAYERS)
        for name, player_id in selected.items()
    }
    retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    OUTPUT.mkdir(exist_ok=True)
    for name, player_id in selected.items():
        workbook = make_workbook(player_id, player_data[name], retrieved)
        filename = OUTPUT / f"{name.replace(' ', '_')}.xlsx"
        workbook.save(filename)
        print(f"Created {filename}")


if __name__ == "__main__":
    main()