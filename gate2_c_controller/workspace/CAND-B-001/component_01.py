def is_low_volatility(current_value, historical_values, window_size, threshold_ratio):
    """
    Determines if a metric is in a low-volatility regime by comparing the 
    current value's deviation from the moving average against a threshold.

    Args:
        current_value (float): The most recent metric value.
        historical_values (list): A list of past metric values.
        window_size (int): The number of periods to calculate the moving average.
        threshold_ratio (float): The percentage (as a decimal) of the moving 
                                 average allowed as a deviation.

    Returns:
        bool: True if the absolute deviation is within the threshold, False otherwise.
    """
    if len(historical_values) < window_size:
        raise ValueError("Insufficient historical data for the specified window size.")

    # Calculate the simple moving average of the last 'window_size' elements
    recent_window = historical_values[-window_size:]
    moving_average = sum(recent_window) / window_size

    # Calculate the absolute deviation from the moving average
    deviation = abs(current_value - moving_average)

    # Determine if the deviation is within the allowed threshold of the average
    return deviation <= (moving_average * threshold_ratio)