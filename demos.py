import streamlit as st
import pandas as pd
import time
from statsbombpy import sb

# py -m pip install streamlit statsbombpy pandas
# py -m streamlit run demos.py


# Getting a dataframe

# df = pd.read_excel("planets.xlsx")
# df = pd.read_sql_table("planets", "sqlite:///planets.db")
# df = pd.read_json("planets.json")
# df = pd.read_csv("demo.cvs")

# 
df = sb.events(match_id=3835331)

st.title("Streamlit Demos")

# Calculating a field
df['time_seconds'] = pd.to_timedelta(df['timestamp']).dt.total_seconds()
df = df[(df['time_seconds'] >= 0) & (df['time_seconds'] <= 4000)]

# Trim down to just the fields we want
df = df[['timestamp', 'time_seconds', 'period', 'player', 'team', 'location',
         'duration', 'shot_body_part', 'shot_deflected', 'shot_end_location',
         'shot_first_time', 'shot_one_on_one', 'shot_outcome',
         'shot_saved_off_target', 'shot_statsbomb_xg', 'shot_technique',
         'shot_type']]

df # Shows the dataframe in the Streamlit app


# Saving cleaned data to a new file
df.to_csv("shot_position.csv", index=False)
df.to_excel("shot_position.xlsx", index=False)
df.to_json("shot_position.json", orient="records")


event_period = st.selectbox("Select event period", ["1","2"])   

# Filter where data is equal to the selected value
df = df[df['period'] == int(event_period)]


# Slider Range
st.subheader("Filter by Slider")
start, end = st.slider("Filter by event time (seconds)", min_value=0,
                               max_value=int(df['time_seconds'].max()), 
                               value=(0, int(df['time_seconds'].max())),
                               step=10)

# Filter where value is between the start and end values
df = df[(df['time_seconds'] >= start) & (df['time_seconds'] <= end)]

# Dropdown list of body parts
st.subheader("Filter by Select Box")
body_part = st.selectbox("Select body part", ["Left Foot", "Right Foot", "Head", "Other"])
try :
    df = df[df['shot_body_part'] == body_part]
except:
    st.warning("No shots found for the selected body part.")
    
    
df # Shows the filtered dataframe in the Streamlit app

