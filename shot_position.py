import streamlit as st
import pandas as pd
import time
from statsbombpy import sb


st.set_page_config(page_title="Football Data Analysis", layout="wide")

st.header("Analyzing Sweden vs Switzerland @ UEFA Women's Euro 2022")

df = sb.events(match_id=3835331)

df['time_seconds'] = pd.to_timedelta(df['timestamp']).dt.total_seconds()
df = df[(df['time_seconds'] >= 0) & (df['time_seconds'] <= 3090)]

# Filter by event type == Shot
df = df[df['type'] == 'Shot']

df = df[['timestamp', 'time_seconds', 'period', 'location','player', 'team', 'duration', 'goalkeeper_shot_saved_off_target', 'pass_assisted_shot_id', 'pass_shot_assist', 'shot_aerial_won', 'shot_body_part', 'shot_deflected', 'shot_end_location', 'shot_first_time', 'shot_freeze_frame', 'shot_key_pass_id', 'shot_one_on_one', 'shot_outcome', 'shot_saved_off_target', 'shot_statsbomb_xg', 'shot_technique', 'shot_type']]

df

df[['location_x', 'location_y']] = pd.DataFrame(df['location'].tolist(), index=df.index)
st.scatter_chart(df, x='location_x', y='location_y',
                 color='shot_outcome',
                 size='shot_body_part',
                 
                 )
