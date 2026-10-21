```python
import numpy as np

class ATRTrailingStop:
    """
    Implements a trailing stop mechanism based on ATR (Average True Range).
    
    Attributes:
        atr_period (int): Lookback period for ATR calculation.
        multiplier (float): Multiplier for the ATR to determine stop distance.
    """
    def __init__(self, atr_period=14, multiplier=2.0):
        self.atr_period = atr_period
        self.multiplier = multiplier
        self.stop_price = None
        self.high_price = -np.inf
        self.low_price = np.inf
        self.atr_values = []

    def update(self, high, low, close, prev_close):
        """
        Updates the trailing stop based on new price data.
        
        Args:
            high (float): Current period high.
            low (float): Current period low.
            close (float): Current period close.
            prev_close (float): Previous period close.
        """
        # Calculate True Range
        tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
        self.atr_values.append(tr)
        
        if len(self.atr_values) > self.atr_period:
            self.atr_values.pop(0)
            
        if len(self.atr_values) < self.atr_period:
            return None

        atr = sum(self.atr_values) / self.atr_period
        offset = atr * self.multiplier

        # Logic for Long Position
        if self.stop_price is None:
            self.stop_price = close - offset
            self.high_price = close
        else:
            self.high_price = max(self.high_price, close)
            new_stop = self.high_price - offset
            # Trailing stop only moves up
            self.stop_price = max(self.stop_price, new_stop)

        return self.stop_price

# Example Usage:
if __name__ == "__main__":
    # Mock data: [High, Low, Close]
    data = [
        (105, 95, 100, 100),
        (108, 98, 106, 100),
        (110, 102, 109, 106),
        (107, 95, 96, 109)
    ]
    
    ts = ATRTrailingStop(atr_period=2, multiplier=1.5)
    for h, l, c, pc in data:
        stop = ts.update(h, l, c, pc)
        print(f"Close: {c}, Stop: {stop:.2f}")
```