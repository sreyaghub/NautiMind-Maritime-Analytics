import pandas as pd


def extract_performance_data(df):

    metrics = {
        "allowed_speed": 0,
        "actual_speed": 0,
        "fuel_consumption": 0,
        "wind_speed": 0,
        "beaufort_scale": 0
    }

    for index, row in df.iterrows():

        try:
            parameter = str(row[1]).strip().upper()

            # ALLOWED CP SPEED
            if "ALLOWED CP SPEED" in parameter:
                for col in row:
                    val = pd.to_numeric(col, errors="coerce")
                    if pd.notna(val) and val > 0:
                        metrics["allowed_speed"] = val
                        break

            # ACTUAL SPEED
            elif "SPEED LAST 24" in parameter or "SPEED MADE GOOD" in parameter:
                for col in row:
                    val = pd.to_numeric(col, errors="coerce")
                    if pd.notna(val) and val > 0:
                        metrics["actual_speed"] = val
                        break

            # FUEL CONSUMPTION
            # Must contain CONS or CONSUMPTION to avoid grabbing ROB rows
            # Range 0 < val < 100 rules out ROB (hundreds of MT)
            elif (
                ("LSFO" in parameter or "HFO" in parameter or "VLSFO" in parameter)
                and ("CONS" in parameter or "CONSUMPTION" in parameter)
            ):
                for col in row:
                    val = pd.to_numeric(col, errors="coerce")
                    if pd.notna(val) and 0 < val < 100:
                        metrics["fuel_consumption"] = val
                        break

            # Fallback: any row with CONSUMPTION and realistic value
            elif "CONSUMPTION" in parameter or "CONS" in parameter:
                if metrics["fuel_consumption"] == 0:
                    for col in row:
                        val = pd.to_numeric(col, errors="coerce")
                        if pd.notna(val) and 0 < val < 100:
                            metrics["fuel_consumption"] = val
                            break

            # WIND SPEED
            elif "WIND SPEED" in parameter:
                for col in row:
                    val = pd.to_numeric(col, errors="coerce")
                    if pd.notna(val) and val > 0:
                        metrics["wind_speed"] = val
                        break

            # BEAUFORT SCALE
            elif "BEAUFORT" in parameter or "BF" == parameter or "B.F" in parameter:
                for col in row:
                    val = pd.to_numeric(col, errors="coerce")
                    if pd.notna(val) and 0 <= val <= 12:
                        metrics["beaufort_scale"] = val
                        break

        except Exception:
            continue

    return metrics