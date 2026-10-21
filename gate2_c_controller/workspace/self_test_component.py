def rolling_mean(values, period):
    if period <= 0:
        raise ValueError("Period must be greater than zero.")
    
    if len(values) < period:
        return None
    
    subset = values[-period:]
    return sum(subset) / period