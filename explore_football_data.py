import streamlit as st
import pandas as pd
import time
from statsbombpy import sb

# py -m pip install streamlit statsbombpy pandas
# py -m streamlit run football_data_task2.py

# Set page config
st.set_page_config(page_title="Football Data Analysis", layout="wide")

# Configure cache for API calls
@st.cache_data
def get_competition_matches():
    """Get all Women's Euro 2022 matches"""
    competitions = sb.competitions()
    # Filter for Women's Euro 2022
    euro22 = competitions[(competitions['competition_name'] == "UEFA Women's Euro") & 
                          (competitions['season_name'] == "2022")]
    
    if len(euro22) > 0:
        comp_id = euro22.iloc[0]['competition_id']
        season_id = euro22.iloc[0]['season_id']
        matches = sb.matches(comp_id, season_id)
        return matches
    return None

@st.cache_data
def get_match_events(match_id: int):
    """Get events for a specific match"""
    return sb.events(match_id=match_id)

@st.cache_data
def get_match_lineups(match_id: int):
    """Get lineups for a specific match"""
    return sb.lineups(match_id=match_id)

# Load matches and create lookup
try:
    matches_df = get_competition_matches()
    if matches_df is not None:
        # Create match lookup dictionary
        EURO22MATCHES = {}
        for _, row in matches_df.iterrows():
            match_name = f"{row['home_team'].replace(' Women\'s', '')} vs {row['away_team'].replace(' Women\'s', '')}"

            EURO22MATCHES[match_name] = row['match_id']
    else:
        st.error("Could not load Women's Euro 2022 matches")
        EURO22MATCHES = {}
except Exception as e:
    st.error(f"Error loading matches: {e}")
    EURO22MATCHES = {}


if EURO22MATCHES == {}:
    exit()

# Title and Introduction
st.title("⚽ Football Data Analysis")
st.header("Women's Euro 2022 matches -  StatsBomb & Pandas")

# Task 2 Section
st.header("Task 1: Find Headed Goals in England vs Sweden Game")

match_name = st.sidebar.selectbox("Select a match to analyze", list(EURO22MATCHES.keys()))

event_type = None
event_type = "Shot"


match_id = EURO22MATCHES.get(match_name)
if match_id is None:
    st.error(f"Match '{match_name}' not found")
else:
    events_df = get_match_events(match_id)

    event_type = st.sidebar.selectbox("Select event type", (["Shot"] if event_type == "Shot" else [] ) +  ["None"] + events_df['type'].unique().tolist())

    if event_type != "None":
        events_df = events_df[events_df['type'] == event_type]

    if event_type == "Shot":
        body_part = st.sidebar.selectbox("Select body part", ["None"] + events_df['shot_body_part'].dropna().unique().tolist())

        shot_outcome = st.sidebar.selectbox("Select shot outcome (if applicable)", ["None"] + events_df['shot_outcome'].dropna().unique().tolist())

        if body_part != "None":
            events_df = events_df[events_df['shot_body_part'] == body_part]

        if shot_outcome != "None":
            events_df = events_df[events_df['shot_outcome'] == shot_outcome]

    if event_type != "None":
        display_df = events_df[['timestamp', 'period', 'player', 'team','duration'] + [col for col in events_df.columns if event_type.lower() in col]].copy()
    else:
        display_df = events_df
    
    st.dataframe(display_df.reset_index(drop=True))




st.divider()

# Extension Section
st.header("Extension: Shots Analysis")

st.markdown("""
**Analyze all shots in the Netherlands vs Sweden game**

Including: player, team, and shot technique
""")
