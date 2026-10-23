python
import pandas as pd

def calculate_candle_metrics(df, window=20):
    """
    Calculates the body-to-range ratio and identifies relative body size.
    
    Parameters:
    df (pd.DataFrame): DataFrame with 'open', 'high', 'low', 'close' columns.
    window (int): Rolling window size for the average body size.
    
    Returns:
    pd.DataFrame: Original df with 'body_ratio' and 'relative_body_size' columns.
    """
    # Calculate absolute body size
    body_size = (df['close'] - df['open']).abs()
    
    # Calculate total range (high - low)
    # Handle cases where range is 0 to avoid division by zero
    candle_range = (df['high'] - df['low']).replace(0, 1e-9)
    
    # Body-to-range ratio (0 to 1)
    df['body_ratio'] = body_size / candle_range
    
    # Relative body size: current body size vs rolling average of body sizes
    rolling_avg_body = body_size.rolling(window=window).mean()
    df['relative_body_size'] = body_size / rolling_avg_body
    
    return df