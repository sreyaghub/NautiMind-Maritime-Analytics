def vessel_score(metrics, analysis):

    allowed = float(
        metrics.get("allowed_speed", 0)
    )

    actual = float(
        metrics.get("actual_speed", 0)
    )

    if allowed == 0:
        return 0

    score = (actual / allowed) * 100

    return round(
        min(score, 100),
        2
    )