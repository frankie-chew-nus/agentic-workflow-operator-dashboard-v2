```python
def calculate_expansion(target_high, target_low, preceding_highs, preceding_lows, period=14):
    """
    Calculates the expansion ratio of a target candle range relative to the 
    arithmetic mean of preceding candle ranges.
    
    :param target_high: High of the current candle
    :param target_low: Low of the current candle
    :param preceding_highs: List of highs for preceding candles
    :param preceding_lows: List of lows for preceding candles
    :param period: Number of preceding candles to consider
    :return: Tuple (target_range, mean_range, expansion_ratio)
    """
    
    # Calculate target range
    target_range = target_high - target_low
    
    # Calculate ranges for the preceding period
    ranges = [h - l for h, l in zip(preceding_highs[-period:], preceding_lows[-period:])]
    
    if not ranges:
        return target_range, 0.0, 0.0
    
    # Calculate arithmetic mean
    mean_range = sum(ranges) / len(ranges)
    
    # Calculate expansion ratio (1.0 = average, >1.0 = expansion, <1.0 = contraction)
    expansion_ratio = target_range / mean_range if mean_range != 0 else 0.0
    
    return target_range, mean_range, expansion_ratio

# Example usage:
# highs = [10, 12, 11, 13, 12]
# lows = [8, 9, 9, 10, 10]
# target_h, target_l = 15, 9
# print(calculate_expansion(target_h, target_l, highs, lows))
```