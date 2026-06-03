import pandas as pd


def _find_row(df, keywords):
    """Return the index of the first row whose col[1] matches any keyword."""
    for index, row in df.iterrows():
        cell = str(row[1]).strip().upper()
        for kw in keywords:
            if kw in cell:
                return index
    return None


def extract_daily_trends(df):

    dates = []
    speeds = []
    fuels = []
    winds = []

    # Dynamically find rows by label instead of hardcoding numbers
    date_row  = _find_row(df, ["DATE", "NOON DATE", "REPORT DATE"])
    speed_row = _find_row(df, ["SPEED LAST 24", "SPEED MADE GOOD", "ACTUAL SPEED"])
    fuel_row  = _find_row(df, ["LSFO", "HFO", "FUEL CONS"])
    wind_row  = _find_row(df, ["WIND SPEED"])

    # Fall back to hardcoded guesses only if scan fails
    if date_row  is None: date_row  = 9
    if speed_row is None: speed_row = 27
    if fuel_row  is None: fuel_row  = 53
    if wind_row  is None: wind_row  = 33

    for col in range(2, df.shape[1]):

        date = df.iloc[date_row, col]

        if str(date) == "nan":
            continue

        dates.append(str(date))
        speeds.append(df.iloc[speed_row, col])
        fuels.append(df.iloc[fuel_row, col])
        winds.append(df.iloc[wind_row, col])

    return {
        "dates": dates,
        "speeds": speeds,
        "fuels": fuels,
        "winds": winds
    }