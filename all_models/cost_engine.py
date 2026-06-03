def calculate_cost_impact(analysis):

    fuel_variance = analysis["fuel_variance"]

    fuel_price = 600

    additional_cost = 0

    if fuel_variance > 0:
        additional_cost = fuel_variance * fuel_price

    return round(additional_cost, 2)