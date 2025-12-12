def gas_to_air_quality_fixed(gas_resistance, min_val=10000, max_val=67000):
    """Normalize gas resistance to Air Quality score (0-100) based on observed range."""
       
    if gas_resistance < min_val:
        gas_resistance = min_val
    if gas_resistance > max_val:
        gas_resistance = max_val
        
    score = (gas_resistance - min_val) / (max_val - min_val) * 100.0
    return round(score, 2)

def air_quality_label(score):
    if score >= 80:
        return "Good"
    elif score >= 60:
        return "Fair"
    elif score >= 40:
        return "Moderate"
    elif score >= 20:
        return "Poor"
    else:
        return "Bad"
