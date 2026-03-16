import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

st.set_page_config(page_title="Sheffield Climate Data", layout="wide")
st.title("Sheffield Climate Data Analysis")

st.markdown("""
This repo has a `/.streamlit/config.toml` file.

It has runOnSave set to true, which means that every time we save a file, 
it will automatically re-run the Streamlit app. 

Just set up VS Code on the left and this Streamlit app on the right and you
can see your changes as you make them!                
""")

df = pd.read_csv("sheffielddata.txt", # I know it's not a csv file but it's close enough
                 sep="  +", # this means split on 2 or more spaces, as the data is separated by multiple spaces
                 skiprows=7, # Skip the first 7 rows which are just text and not data
                 names=["Year",
                        "Month",
                        "MaxTempC",
                        "MinTempC",
                        "AirFrostDays",
                        "RainfallMM",
                        "SunshineHours",
                        "DataQuality"],
                 na_values = "---") # Convert --- to NaN (missing value)
# so these values will be ignored in calculations

number_cols = ["MaxTempC", "MinTempC", "AirFrostDays", "RainfallMM", "SunshineHours"]
# Convert the numbers_cols to pure numbers
# ignoring the estimation of values marked with "*"
# and the notes marked with "#"
df[number_cols] = df[number_cols].apply(pd.to_numeric, errors="coerce") 

st.subheader("Data from 'sheffielddata.txt' has been loaded and cleaned.")
st.write(df)

st.subheader("Example - Most Sunshine Month/Year:")
sunniest = df[df["SunshineHours"] == df["SunshineHours"].max()]
sunniest  # Prints it out as a dataframe, but we can also select specific columns to print out


col1, col2 = st.columns(2)
col1.metric(label="Sunniest Month/Year",
            value=f"{sunniest['Month'].values[0]}/{sunniest['Year'].values[0]}")
col2.metric(label="Sunniest Month Hours", value=sunniest['SunshineHours'])

st.header("Data Tasks")
st.subheader("Task 1 - Output climate for 1884 and 1984")

st.subheader("Task 2 - Calculate Difference in temperature between 1884 and 1984. Which was Hotter/Cooler?")

st.subheader("Task 3 - Find which month/year was the Coldest?")

st.subheader("Task 4 - Find which month/year was the Hottest?")

st.subheader("Task 5 - Which month/year had the most rainfall?")

st.header("User Input Tasks")
st.subheader("Task 6 - Get user to input a year and output that year")
# Look at st.number_input and st.selectbox for this task

st.subheader("Task 7 - Get user to input a Month and output that Month for past 10 years")
# Look at st.selectbox

st.header("Graphing Tasks - Streamlit")
st.subheader("Example - Calculate the average rainfall and  for each month and graph it as a bar chart")
avg_rainfall = df.groupby("Month")["RainfallMM"].mean().reset_index()
avg_rainfall

st.bar_chart(avg_rainfall, x="Month", y="RainfallMM", width="stretch")


st.subheader("Example - Graphing the minimum and maximum temperature for July by year as a line chart:")
july_data = df[df["Month"] == 7]
st.line_chart(july_data, x="Year", y=["MinTempC", "MaxTempC"])

st.subheader("Task 8 - Calculate the average minimum and maximum temperature for each month as table and graph it as a line chart with error lines showing the standard deviation")
st.write("Hint: use groupby and mean(), you might want to do 2 charts for min and max temperature, or you can do them on the same chart but use the hue parameter to show them as different colours")

st.header("Graphing Tasks - Matplotlib")
st.subheader("Example - Graphing the rainfall for January by year as a line chart:")
january_data = df[df["Month"] == 1]
plt.figure(figsize=(10, 5),clear=True)
plt.plot(january_data["Year"], january_data["RainfallMM"], marker='o')
plt.title("Rainfall for January by Year")
plt.xlabel("Year")
plt.ylabel("Rainfall (mm)")
st.pyplot(plt,width="stretch", clear_figure =True)


st.header("Graphing Tasks - Seaborn")

st.subheader("Example - Is there a correlation between sunshine hours and maximum temperature:")
sns.scatterplot(data=df, x="SunshineHours", y="MaxTempC", hue="Year", legend=True)
plt.title("Sunshine Hours vs Max Temperature")
st.pyplot(plt,width="stretch", clear_figure =True)

st.subheader("Example - Graphing the min & max temperature for each month as a line chart with error lines with a scatter plot of all the data which shows the year by colour:")
sns.lineplot(data=df, x="Month", y="MinTempC", ci="sd", label="Min Temp")
sns.lineplot(data=df, x="Month", y="MaxTempC", ci="sd", label="Max Temp")
sns.scatterplot(data=df, x="Month", y="MinTempC", hue="Year", palette="viridis", legend=True, alpha=0.6)
sns.scatterplot(data=df, x="Month", y="MaxTempC", hue="Year", palette="magma", legend=True, alpha=0.6)
plt.title("Min & Max Temperature by Month with Year as Colour")
st.pyplot(plt,width="stretch", clear_figure =True)

st.subheader("Task 9 - What does the graph above show about change in temperatures?")
st.text("""Add graphs / stats we could use to show this more clearly?""")