"""Search for an NBA player and download their season statistics."""

from datetime import datetime, timezone
from io import BytesIO
from pathlib import Path
import re
from urllib.error import URLError
from urllib.parse import urlencode

import pandas as pd
import plotly.express as px
import streamlit as st

from create_nba_workbooks import HEADERS, get_json, load_player, make_workbook


SEARCH_URL = "https://site.web.api.espn.com/apis/search/v2"


def search_players(query):
	params = urlencode({"query": query, "type": "player", "limit": 50})
	data = get_json(f"{SEARCH_URL}?{params}")
	players = []
	seen_ids = set()
	for group in data.get("results", []):
		if group.get("type") != "player":
			continue
		for player in group.get("contents", []):
			match = re.search(r"(?:^|~)a:(\d+)(?:~|$)", player.get("uid", ""))
			if player.get("defaultLeagueSlug") != "nba" or not match:
				continue
			player_id = int(match.group(1))
			if player_id not in seen_ids and player.get("displayName"):
				players.append({
					"id": player_id,
					"name": player["displayName"],
					"team": player.get("subtitle") or "Team unavailable",
				})
				seen_ids.add(player_id)
	return players


st.set_page_config(page_title="NBA Players Statistics by Season")
st.sidebar.image(str(Path(__file__).with_name("UTC Sheffield Olympic Legacy Park - Horizontal.png")), width="stretch")
st.sidebar.image("https://upload.wikimedia.org/wikipedia/en/0/03/National_Basketball_Association_logo.svg", width="stretch")
st.title("NBA Players Statistics by Season")

with st.form("player_search"):
	query = st.text_input("Player name", placeholder="e.g. Kobe Bryant")
	submitted = st.form_submit_button("Search")

if submitted:
	st.session_state.pop("workbook", None)
	st.session_state["players"] = []
	if not query.strip():
		st.warning("Enter a player name.")
	else:
		try:
			with st.spinner("Searching players..."):
				st.session_state["players"] = search_players(query.strip())
			if not st.session_state["players"]:
				st.info("No NBA players found. Try another name.")
		except (URLError, TimeoutError, ValueError, KeyError, OSError):
			st.error("Player search is unavailable. Please try again later.")

players = st.session_state.get("players", [])
if players:
	player = st.selectbox(
		"Player",
		players,
		format_func=lambda item: f"{item['name']} | {item['team']} | ID {item['id']}",
	)
	if st.button("Get season statistics", type="primary"):
		st.session_state.pop("workbook", None)
		try:
			with st.spinner("Loading season statistics..."):
				rows = load_player(player["name"], player["id"], active=False)
				retrieved = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
				workbook = make_workbook(player["id"], rows, retrieved)
				output = BytesIO()
				workbook.save(output)
				filename = re.sub(r"[^\w.-]+", "_", player["name"]).strip("_") + ".xlsx"
				st.session_state["workbook"] = {
					"player_id": player["id"],
					"filename": filename,
					"data": output.getvalue(),
					"rows": rows,
				}
		except (URLError, TimeoutError, ValueError, KeyError, OSError, IndexError):
			st.error("Season statistics are unavailable for this player. Try another player or try again later.")

	result = st.session_state.get("workbook")
	if result and result["player_id"] == player["id"]:
		st.caption("Regular-season and playoff statistics. The current season may be incomplete.")
		df = pd.DataFrame(result["rows"], columns=HEADERS)
		st.dataframe(df, hide_index=True, width="stretch")
		st.download_button(
			"Download Excel workbook",
			data=result["data"],
			file_name=result["filename"],
			mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
		)
		
		# Career stats scatter graph
		if not df.empty:
			st.subheader("Career Stats Scatter Graph")
			
			y_stat = st.selectbox(
				"Y-axis statistic",
				["Points", "Rebounds", "Assists", "Games", "Steals", "Blocks", "3-Pointers Made"],
				index=0
			)
			
			# Extract year from season (e.g., "2020-21" -> 2020)
			graph_df = df.copy()
			graph_df["Year"] = graph_df["Season"].str[:4].astype(int)
			
			fig = px.scatter(
				graph_df,
				x="Year",
				y=y_stat,
				color="Game Type",
				symbol="Game Type",
				hover_data=["Season", "Team", "Games"],
				title=f"{player['name']} - Career {y_stat} by Year",
				labels={"Year": "Season Year", y_stat: y_stat},
				color_discrete_map={"Regular season": "#1f77b4", "Playoffs": "#ff7f0e"},
				symbol_map={"Regular season": "circle", "Playoffs": "diamond"},
				size_max=10,
			)
			fig.update_layout(height=500, showlegend=True)
			fig.update_xaxes(type="linear")
			st.plotly_chart(fig, width='stretch')
