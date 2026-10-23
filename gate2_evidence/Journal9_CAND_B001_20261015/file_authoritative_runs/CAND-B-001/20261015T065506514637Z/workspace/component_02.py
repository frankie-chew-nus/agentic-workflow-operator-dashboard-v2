python
import pandas as pd

def get_volatility_regime(data: pd.Series, period: int = 14, ma_type: str = 'sma') -> pd.Series:
    """
    Identifies volatility regimes by comparing ATR to its own moving average.
    
    Returns:
        pd.Series: 1 for High Volatility (ATR > MA), 0 for Low Volatility (ATR <= MA).
    """
    # Calculate ATR (assuming data is a DataFrame with High, Low, Close)
    # If input is just a Series, this assumes it's already the ATR values
    atr = data
    
    if ma_type == 'ema':
        atr_ma = atr.ewm(span=period, adjust=False).mean()
    else:
        atr_ma = atr.rolling(window=period).mean()
        
    return (atr > atr_ma).astype(int)