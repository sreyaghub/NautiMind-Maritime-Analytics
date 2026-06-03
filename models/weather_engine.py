def calculate_beaufort(wind_speed):
    if wind_speed < 1:
        return 0
    elif wind_speed < 4:
        return 1
    elif wind_speed < 7:
        return 2
    elif wind_speed < 11:
        return 3
    elif wind_speed < 17:
        return 4
    elif wind_speed < 22:
        return 5
    else:
        return 6


def weather_risk(metrics):
    # Extract wind speed and ensure it's a float
    wind = float(metrics.get("wind_speed", 0))
    
    # Dynamically calculate Beaufort scale based on the wind speed
    metrics["beaufort_scale"] = calculate_beaufort(wind)
    
    # Grab the newly calculated value for risk logic
    beaufort = float(metrics["beaufort_scale"])

    # Risk evaluation logic
    if wind > 20 or beaufort >= 6:
        return "HIGH"

    elif wind > 10 or beaufort >= 4:
        return "MEDIUM"

    else:
        return "LOW"