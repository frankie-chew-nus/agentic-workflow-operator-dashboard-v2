```python
import pandas as pd
import numpy as np

def calculate_candle_metrics(df, lookback=20, std_dev_threshold=2.0):
    """
    Calculates body-to-range ratios and identifies relative body size outliers.
    
    Expected columns in df: ['open', 'high', 'low', 'close']
    
    :param df: DataFrame containing OHLC data
    :param lookback: Rolling window for outlier detection
    :param std_dev_threshold: Z-score threshold to define an outlier
    :return: DataFrame with 'body_ratio' and 'is_body_outlier' columns
    """
    df = df.copy()
    
    # Calculate absolute body size and total range
    body_size = (df['close'] - df['open']).abs()
    total_range = df['high'] - df['low']
    
    # Avoid division by zero for flat candles
    df['body_ratio'] = body_size / total_range.replace(0, np.nan)
    
    # Calculate rolling statistics for body size
    rolling_mean = body_size.rolling(window=lookback).mean()
    rolling_std = body_size.rolling(window=lookback).std()
    
    # Identify outliers (Z-score > threshold)
    z_scores = (body_size - rolling_mean) / rolling_std
    df['is_body_outlier'] = z_scores > std_dev_threshold
    
    return df

# Example usage:
if __name__ == "__main__":
    # Mock data
    data = {
        'open': [100, 102, 101, 105, 110],
        'high': [105, 103, 106, 115, 112],
        'low': [99, 100, 98, 104, 108],
        'close': [102, 101, 105, 112, 109]
    }
    df_candles = pd.DataFrame(data)
    
    results = calculate_candle_metrics(df_candles, lookback=3)
    print(results[['body_ratio', 'is_body_outlier']])
```