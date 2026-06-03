def analyze_performance(metrics):

    try:
        allowed_speed = float(
            metrics.get("allowed_speed", 0)
        )
    except:
        allowed_speed = 0

    try:
        actual_speed = float(
            metrics.get("actual_speed", 0)
        )
    except:
        actual_speed = 0

    try:
        fuel_consumption = float(
            metrics.get("fuel_consumption", 0)
        )
    except:
        fuel_consumption = 0

    speed_variance = round(
        actual_speed - allowed_speed,
        2
    )

    fuel_variance = round(
        fuel_consumption - 12,
        2
    )

    if speed_variance < 0:
        speed_status = "Under Speed"
    elif speed_variance > 0:
        speed_status = "Over Speed"
    else:
        speed_status = "On Speed"

    if fuel_variance > 0:
        fuel_status = "Over Consumption"
    else:
        fuel_status = "Normal"

    return {
        "speed_variance": speed_variance,
        "fuel_variance": fuel_variance,
        "speed_status": speed_status,
        "fuel_status": fuel_status
    }