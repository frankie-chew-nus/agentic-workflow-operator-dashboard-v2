```python
import pandas as pd
import numpy as np

def get_volatility_regime(data: pd.Series, window: int = 20, ma_type: str = 'sma'):
    """
    Identifies volatility regimes based on a rolling window comparison.
    
    Parameters:
    data (pd.Series): Price data or returns.
    window (int): Lookback period for volatility and its moving average.
    ma_type (str): 'sma' for Simple Moving Average, 'ema' for Exponential.
    
    Returns:
    pd.DataFrame: Contains 'volatility', 'vol_ma', and 'regime' (1 for High, 0 for Low).
    """
    # Calculate rolling volatility (standard deviation of returns)
    returns = data.pct_change().dropna()
    vol = returns.rolling(window=window).std()
    
    # Calculate moving average of the volatility
    if ma_type == 'ema':
        vol_ma = vol.ewm(span=window, adjust=False).mean()
    else:
        vol_ma = vol.rolling(window=window).mean()
        
    # Regime: 1 if current vol > average vol (High Vol), else 0 (Low Vol)
    regime = (vol > vol_ma).astype(int)
    
    return pd.DataFrame({
        'volatility': vol,
        'vol_ma': vol_ma,
        'regime': regime
    })

# Example usage:
# df = get_volatility_regime(price_series, window=20)
```