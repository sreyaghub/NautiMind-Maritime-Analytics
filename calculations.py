def calculate_performance_score(actual_speed, allowed_speed):

    try:
        actual_speed = float(actual_speed)
        allowed_speed = float(allowed_speed)

        if allowed_speed == 0:
            return 0

        return round(
            (actual_speed / allowed_speed) * 100,
            2
        )

    except:
        return 0


def calculate_speed_variance(
    actual_speed,
    allowed_speed
):

    try:
        return round(
            float(actual_speed)
            - float(allowed_speed),
            2
        )

    except:
        return 0


def calculate_fuel_variance(
    actual_fuel,
    benchmark_fuel=12
):

    try:
        return round(
            float(actual_fuel)
            - float(benchmark_fuel),
            2
        )

    except:
        return 0


def calculate_monthly_saving(
    fuel_variance,
    fuel_price=600
):

    try:
        return round(
            abs(float(fuel_variance))
            * 30
            * float(fuel_price),
            2
        )

    except:
        return 0