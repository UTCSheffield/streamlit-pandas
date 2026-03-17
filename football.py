import streamlit as st
import pandas as pd
import time
from statsbombpy import sb

# py -m pip install streamlit statsbombpy pandas
# py -m streamlit run football.py

# Set page config
st.set_page_config(page_title="Football Data Analysis", layout="wide")

COMPETITION ="UEFA Women's Euro"
SEASON = "2022"

# Configure cache for API calls
@st.cache_data
def get_competition_matches():
    """Get all Women's Euro 2022 matches"""
    competitions = sb.competitions()
    
    # Filter for Women's Euro 2022
    euro22 = competitions[(competitions['competition_name'] == COMPETITION) & 
                          (competitions['season_name'] == SEASON)]
    
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
            match_name = f"""{row['home_team'].replace(" Women's", "")} vs {row['away_team'].replace(" Women's", "")}"""

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
body_part = "None"
shot_outcome = "None"


match_id = EURO22MATCHES.get(match_name)
if match_id is None:
    st.error(f"Match '{match_name}' not found")
else:
    
    st.header(f"Analyzing {match_name} - Match ID: {match_id}")
    
    df = get_match_events(match_id)
    
    df['time_seconds'] = pd.to_timedelta(df['timestamp']).dt.total_seconds()
    
    event_period = st.sidebar.selectbox("Select event period", ["None"] + df['period'].dropna().unique().tolist())   
    
    time_filter = st.sidebar.slider("Filter by event time (seconds)", min_value=0, max_value=int(df['time_seconds'].max()), value=(0, int(df['time_seconds'].max())), step=10)  
    df = df[(df['time_seconds'] >= time_filter[0]) & (df['time_seconds'] <= time_filter[1])]

    event_type = st.sidebar.selectbox("Select event type", (["Shot"] if event_type == "Shot" else [] ) +  ["None"] + df['type'].unique().tolist())

    if event_period != "None":
        df = df[df['period'] == event_period]
        
    if event_type != "None":
        df = df[df['type'] == event_type]

    if event_type == "Shot":
        body_part = st.sidebar.selectbox("Select body part", ["None"] + df['shot_body_part'].dropna().unique().tolist())

        shot_outcome = st.sidebar.selectbox("Select shot outcome (if applicable)", ["None"] + df['shot_outcome'].dropna().unique().tolist())

        if body_part != "None":
            df = df[df['shot_body_part'] == body_part]

        if shot_outcome != "None":
            df = df[df['shot_outcome'] == shot_outcome]

    if event_type != "None":
        df_fields = ['timestamp',
                     'time_seconds',
                     'period',
                     'player', 
                     'team', 
                     'location',
                     'duration'
                     ] + [col for col in df.columns if event_type.lower() in col]
        
        display_df = df[df_fields].copy()
    else:
        display_df = df
    
    st.dataframe(display_df.reset_index(drop=True))

st.divider()

# Extension Section
st.header("Extension: Shots Analysis")

st.markdown("""
**Analyze all shots in the Netherlands vs Sweden game**

Including: player, team, and shot technique
""")



st.markdown("""
**Analyze all passes in the Netherlands vs Sweden game**

Including: player, team, and pass technique
""")

st.header("Simplified Code Used for Analysis")

code_string = f"""
import streamlit as st
import pandas as pd
import time
from statsbombpy import sb


st.set_page_config(page_title="Football Data Analysis", layout="wide")

st.header("Analyzing {match_name} @ {COMPETITION} {SEASON}")

df = sb.events(match_id={match_id})
"""

if event_period != "None":
    code_string += f"""
# Filter by event period == {event_period}
df = df[df['period'] == {event_period}]
"""

code_string += f"""
df['time_seconds'] = pd.to_timedelta(df['timestamp']).dt.total_seconds()
df = df[(df['time_seconds'] >= {time_filter[0]}) & (df['time_seconds'] <= {time_filter[1]})]
"""

if event_type != "None":
    code_string += f"""
# Filter by event type == {event_type}
df = df[df['type'] == '{event_type}']
"""

if body_part != "None":
    code_string += f"""
# Filter by body part == {body_part}    
df = df[df['shot_body_part'] == '{body_part}']
"""

if shot_outcome != "None":
    code_string += f"""
# Filter by shot outcome == {shot_outcome}
df = df[df['shot_outcome'] == '{shot_outcome}']
"""

if event_type != "None":
    code_string += f"""
df = df[{repr(df_fields)}]
"""        

code_string += f"""
df

"""
    
st.code(code_string, language="python")