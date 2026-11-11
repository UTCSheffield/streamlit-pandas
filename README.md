# Streamlit Pandas Demos and Exercises

## Installation

### General Setup
```bash
pip install -r requirements.txt
```

### UTC Sheffield
Due to system restrictions, use:
```bash
py -m pip install -r requirements.txt
```

## Running Files

### General
```bash
streamlit run <filename.py>
```

### UTC Sheffield
```bash
py -m streamlit run <filename.py>
```

## Available Files

- **demos.py** - Demonstrates streamlit and pandas functionality
- **planets.py** - Uses streamlit and pandas to explore planets data
- **football.py** - Uses streamlit and pandas to explore football data
- **climate.py** - Uses streamlit and pandas to explore Sheffield climate data 
and is where the main tasks are

## NBA Excel Practice

The `nba_workbooks` folder contains individual workbooks for ten current players,
plus Michael Jordan and Kobe Bryant. Each has one Seasons sheet with the same
columns, so students can choose their favourite player and use the same formulas.

The numbers are ESPN regular-season and playoff totals, except Minutes Per Game,
which is ESPN's rounded per-game average. The source and retrieval date are
stored in each workbook's properties. Game Type distinguishes regular
season from playoffs, which have separate rows. A season with a team change has
one row per team and game type; combined team rows are omitted to avoid double
counting. Some players have no playoff rows. The latest season may be incomplete.
The players are well-known active players, not a verified popularity ranking.
Use Game Type as a condition when calculating regular-season or playoff totals
separately; summing all rows includes both.

To search for another NBA player and download a workbook with the same columns,
run `streamlit run nba.py`. The search and statistics require internet access.

To refresh all the files (requires internet access and `openpyxl`):

```bash
python create_nba_workbooks.py
```


## Requirements

See `requirements.txt` for dependencies (typically streamlit and pandas).