```python
def metadata():
    return {
        "name": "ExhaustionPriceReversion",
        "version": "v2.1.1",
        "description": "Mean reversion strategy based on exhaustion candles in low-volatility regimes."
    }

def parameter_schema():
    return {
        "atr_period": {"type": "int", "min": 10, "max": 20},
        "body_multiplier": {"type": "float", "min": 1.2, "max": 2.0},
        "risk_reward_ratio": {"type": "float", "min": 1.5, "max": 3.0}
    }

def prepare(history):
    # Calculate ATR and moving average of ATR
    atr = []
    for i in range(len(history)):
        if i == 0:
            atr.append(0.0)  # Initial ATR value
        else:
            # Implement ATR calculation logic
            pass
    
    # Calculate body sizes and identify exhaustion candles
    exhaustion_candles = []
    for candle in history:
        # Implement body size calculation and exhaustion logic
        pass
    
    return {
        "atr_values": atr,
        "exhaustion_flags": exhaustion_candles
    }

def signal(history, prepared, params):
    signals = []
    atr_period = params.get("atr_period", 14)
    body_multiplier = params.get("body_multiplier", 1.5)
    risk_reward_ratio = params.get("risk_reward_ratio", 1.5)
    
    # Check market regime
    current_atr = prepared["atr_values"][-1] if prepared else 0
    ma_atr = prepared["ma_atr"][-1] if prepared else 0
    
    if current_atr < ma_atr:
        # Low volatility regime - proceed with strategy
        last_candle = history[-1] if history else {}
        
        if last_candle.get("is_bullish_exhaustion"):
            # Bearish exhaustion pattern
            if history[-1]["close"] > last_candle["high"]:
                signals.append({"type": "long", "entry": history[-2]["high"], "exit": history[-2]["low"] * 0.5})
        elif last_candle.get("is_bearish_exhaustion"):
            # Bullish exhaustion pattern
            if history[-1]["close"] < last_candle["low"]:
                signals.append({"type": "short", "entry": history[-2]["low"], "exit": history[-2]["high"] * 0.5})
    
    return signals
```