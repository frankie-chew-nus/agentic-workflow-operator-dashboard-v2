This implementation provides the complete local strategy module. Since the provided utility `UTL-001` is designed for deviation checking, I will implement a specialized internal function for the specific low-volatility regime check required by the hypothesis (`ATR < MA(ATR)`), while still adhering to the local, self-contained nature of the solution.

```python
import math
from typing import List, Dict, Any, Tuple

# --- Helper Functions (Internal Local Utilities) ---

def calculate_atr(history: List[Dict[str, Any]], period: int) -> List[float]:
    """
    Calculates the Average True Range (ATR) for the given history.
    ATR is calculated based on the True Range (TR) of each candle.
    """
    if len(history) < period:
        return [None] * len(history)

    true_ranges = []
    for i in range(len(history)):
        if i == 0:
            # Cannot calculate TR for the first candle
            true_ranges.append(None)
            continue
        
        # Calculate True Range (TR)
        tr1 = abs(history[i]['high'] - history[i]['low'])
        tr2 = abs(history[i]['high'] - history[i-1]['close'])
        tr3 = abs(history[i]['low'] - history[i-1]['close'])
        
        true_range = max(tr1, tr2, tr3)
        true_ranges.append(true_range)

    # Calculate ATR (Simple Moving Average of TR)
    atr_values = [None] * period
    for i in range(period, len(history)):
        # Calculate the average of the last 'period' true ranges
        recent_tr = true_ranges[i-period:i]
        atr = sum(recent_tr) / period
        atr_values.append(atr)
        
    # Pad the beginning with None values
    return [None] * (period - 1) + atr_values[period - 1:]


def is_low_volatility_regime(atr_values: List[float], window_size: int = 20) -> List[bool]:
    """
    Implements the specific low-volatility regime check: ATR(14) < 20-period MA(ATR(14)).
    This is a specialized local implementation of the hypothesis filter.
    """
    if not atr_values:
        return []
    
    regime_status = [False] * len(atr_values)
    
    # We need at least 'window_size' data points to calculate the MA
    for i in range(window_size, len(atr_values)):
        current_atr = atr_values[i]
        
        # Calculate the Simple Moving Average of the last 'window_size' ATR values
        recent_atr = atr_values[i - window_size:i]
        moving_average_atr = sum(recent_atr) / window_size
        
        # Check the hypothesis condition: ATR < MA(ATR)
        if current_atr is not None and current_atr < moving_average_atr:
            regime_status[i] = True
            
    return regime_status


def classify_exhaustion_candle(candle: Dict[str, Any], body_multiplier: float, avg_body_size: float) -> Tuple[bool, bool]:
    """
    UTL-002: Classifies a candle as Bullish or Bearish exhaustion.
    Returns (is_bullish_exhaustion, is_bearish_exhaustion)
    """
    open_p = candle['open']
    close_p = candle['close']
    high_p = candle['high']
    low_p = candle['low']
    
    body_size = abs(close_p - open_p)
    range_size = high_p - low_p
    
    if range_size == 0:
        return False, False

    # 1. Check Body Size requirement
    if body_size <= body_multiplier * avg_body_size:
        return False, False

    # 2. Check Exhaustion Ratio requirement
    # Bullish exhaustion: (Close - Open) / (High - Low) < 0.2 AND (Close - Open) > 0
    is_bullish = (close_p - open_p) / range_size < 0.2 and (close_p - open_p) > 0
    
    # Bearish exhaustion: (Open - Close) / (High - Low) < 0.2 AND (Open - Close) > 0
    is_bearish = (open_p - close_p) / range_size < 0.2 and (open_p - close_p) > 0
    
    return is_bullish, is_bearish


# --- Strategy Module Implementation ---

class ExhaustionMeanReversionStrategy:
    
    def __init__(self, candidate_data: Dict[str, Any]):
        self.candidate = candidate_data
        self.atr_period = 14 # Fixed ATR period for calculation
        self.volatility_window = 20 # Fixed MA window for regime check

    def metadata(self) -> Dict[str, Any]:
        """Provides top-level metadata for the strategy."""
        return {
            "strategy_id": self.candidate['candidate_id'],
            "version": self.candidate['version'],
            "domain": self.candidate['research_domain'],
            "hypothesis": self.candidate['hypothesis'],
            "description": "Mean reversion strategy filtered by low volatility regime.",
            "required_inputs": self.candidate['required_inputs']
        }

    def parameter_schema(self) -> Dict[str, Any]:
        """Defines the schema for tunable parameters."""
        return {
            "atr_period": {"type": "int", "default": 14, "range": self.candidate['parameter_ranges']['atr_period']},
            "body_multiplier": {"type": "float", "default": 1.5, "range": self.candidate['parameter_ranges']['body_multiplier']},
            "risk_reward_ratio": {"type": "float", "default": 2.0, "range": self.candidate['parameter_ranges']['risk_reward_ratio']}
        }

    def prepare(self, history: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Pre-processes the historical data by calculating necessary indicators.
        Returns a dictionary containing the processed data and derived metrics.
        """
        if not history:
            return {"processed_history": [], "atr_values": [], "avg_body_sizes": []}

        # 1. Calculate ATR
        atr_values = calculate_atr(history, self.atr_period)
        
        # 2. Calculate Average Body Size (for exhaustion candle definition)
        body_sizes = [abs(h['close'] - h['open']) for h in history]
        avg_body_sizes = []
        for i in range(len(history)):
            if i < 10:
                avg_body_sizes.append(None)
            else:
                # Average of the last 10 body sizes
                avg_body = sum(body_sizes[i-10:i]) / 10
                avg_body_sizes.append(avg_body)

        # 3. Combine data into a processed structure
        processed_history = []
        for i in range(len(history)):
            processed_history.append({
                **history[i],
                "atr": atr_values[i],
                "avg_body_size": avg_body_sizes[i]
            })
            
        return {
            "processed_history": processed_history,
            "atr_values": atr_values,
            "avg_body_sizes": avg_body_sizes
        }

    def signal(self, history: List[Dict[str, Any]], prepared: Dict[str, Any], params: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Generates trading signals based on the prepared data and parameters.
        """
        processed_history = prepared['processed_history']
        atr_values = prepared['atr_values']
        avg_body_sizes = prepared['avg_body_sizes']
        
        # 1. Apply Low Volatility Regime Filter (UTL-001 adaptation)
        regime_status = is_low_volatility_regime(atr_values, self.volatility_window)
        
        signals = []
        
        # We need at least 2 candles to check for exhaustion followed by a breakout
        for i in range(1, len(processed_history)):
            current_candle = processed_history[i]
            previous_candle = processed_history[i-1]
            
            # Check Regime Filter (Step 2)
            if not regime_status[i]:
                continue
            
            # --- Step 3: Identify Exhaustion Candle (Previous Candle) ---
            
            # Ensure we have valid data for body size calculation
            if previous_candle['avg_body_size'] is None or previous_candle['atr'] is None:
                continue
                
            is_bullish_exhaustion, is_bearish_exhaustion = classify_exhaustion_candle(
                previous_candle, 
                params['body_multiplier'], 
                previous_candle['avg_body_size']
            )
            
            if not (is_bullish_exhaustion or is_bearish_exhaustion):
                continue
                
            # --- Step 4 & 5: Check Breakout and Execute Logic (Current Candle) ---
            
            signal_details = {
                "timestamp": current_candle['timestamp'],
                "signal_type": None,
                "entry_price": None,
                "stop_loss": None,
                "take_profit": None,
                "reason": ""
            }
            
            # Case 1: Bearish Exhaustion -> Short Entry (Break below Low)
            if is_bearish_exhaustion:
                # Entry condition: Price breaks below Low of exhaustion candle
                if current_candle['low'] < previous_candle['low']:
                    
                    # Calculate Risk Parameters (UTL-004)
                    atr_val = previous_candle['atr']
                    risk_amount = atr_val * 1.5 # SL = 1.5 * ATR(14)
                    
                    # Short trade: Entry at current candle's low (or close, for simplicity)
                    entry_price = current_candle['low']
                    stop_loss = entry_price + risk_amount # SL is above entry
                    take_profit = entry_price - (risk_amount * params['risk_reward_ratio'])
                    
                    signal_details.update({
                        "signal_type": "SHORT",
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "reason": "Bearish exhaustion followed by breakout below low in low-volatility regime."
                    })
                    signals.append(signal_details)

            # Case 2: Bullish Exhaustion -> Long Entry (Break above High)
            elif is_bullish_exhaustion:
                # Entry condition: Price breaks above High of exhaustion candle
                if current_candle['high'] > previous_candle['high']:
                    
                    # Calculate Risk Parameters (UTL-004)
                    atr_val = previous_candle['atr']
                    risk_amount = atr_val * 1.5 # SL = 1.5 * ATR(14)
                    
                    # Long trade: Entry at current candle's high (or close, for simplicity)
                    entry_price = current_candle['high']
                    stop_loss = entry_price - risk_amount # SL is below entry
                    take_profit = entry_price + (risk_amount * params['risk_reward_ratio'])
                    
                    signal_details.update({
                        "signal_type": "LONG",
                        "entry_price": entry_price,
                        "stop_loss": stop_loss,
                        "take_profit": take_profit,
                        "reason": "Bullish exhaustion followed by breakout above high in low-volatility regime."
                    })
                    signals.append(signal_details)
                    
        return signals

# --- Execution Example ---

if __name__ == '__main__':
    # Mock Data Generation (Simulating 50 candles)
    mock_history = []
    import random
    base_price = 1900.0
    for i in range(50):
        # Simulate price movement with some volatility
        change = random.uniform(-0.5, 0.5)
        open_p = base_price + change
        high_p = open_p + random.uniform(0.1, 0.5)
        low_p = open_p - random.uniform(0.1, 0.5)
        close_p = open_p + random.uniform(-0.2, 0.2)
        
        mock_history.append({
            "timestamp": f"T{i}",
            "open": round(open_p, 2),
            "high": round(high_p, 2),
            "low": round(low_p, 2),
            "close": round(close_p, 2)
        })
        base_price = close_p

    # Initialize Strategy
    strategy = ExhaustionMeanReversionStrategy(candidate_data={
      "candidate_id": "CAND-B-001",
      "version": "v2.1.1",
      "research_domain": "XAUUSD M1 Price Action",
      "hypothesis": "Mean reversion of M1 price action following an exhaustion candle is more statistically significant when filtered by a low-volatility regime.",
      "evidence_refs": ["SRC-A-003"],
      "operator_assumptions": {"market_regime_definition": "ATR(14) < 20-period moving average of ATR(14)"},
      "candle_definition": "Exhaustion candle: Bullish if (Close - Open) / (High - Low) < 0.2 and (Close - Open) > 0; Bearish if (Open - Close) / (High - Low) < 0.2 and (Open - Close) > 0; Body size > 1.5 * Average(abs(Close - Open), 10).",
      "entry_logic": "Enter long if exhaustion candle is bearish and price breaks above High of exhaustion candle; enter short if exhaustion candle is bullish and price breaks below Low of exhaustion candle.",
      "exit_logic": "Fixed stop loss at 1.5 * ATR(14); take profit at 2.0 * risk.",
      "parameter_ranges": {
        "atr_period": [10, 20],
        "body_multiplier": [1.2, 2.0],
        "risk_reward_ratio": [1.5, 3.0]
      },
      "context_filters": "Low-volatility regime required: ATR(14) < 20-period moving average of ATR(14).",
      "required_inputs": ["Open", "High", "Low", "Close", "ATR"],
      "prohibited_dependencies": ["Martingale", "Grid", "Averaging-down", "Machine Learning"],
      "unresolved_questions": ["Does the M1 noise floor render the exhaustion signal statistically indistinguishable from random walk?"]
    })

    print("==================================================")
    print("           STRATEGY METADATA")
    print("==================================================")
    print(strategy.metadata())
    
    print("\n==================================================")
    print("           PARAMETER SCHEMA")
    print("==================================================")
    print(strategy.parameter_schema())

    # Define parameters for the run
    run_params = {
        "atr_period": 14,
        "body_multiplier": 1.8, # Using a mid-range value
        "risk_reward_ratio": 2.5
    }
    
    print("\n==================================================")
    print(f"           PREPARING DATA (ATR & Body Size)")
    print("==================================================")
    prepared_data = strategy.prepare(mock_history)
    
    print("\n==================================================")
    print("             GENERATING SIGNALS")
    print("==================================================")
    signals = strategy.signal(mock_history, prepared_data, run_params)
    
    if signals:
        print(f"✅ Found {len(signals)} valid trading signals.")
        for i, signal in enumerate(signals):
            print(f"\n--- Signal {i+1} ({signal['signal_type']}) ---")
            print(f"Time: {signal['timestamp']}")
            print(f"Reason: {signal['reason']}")
            print(f"Entry: {signal['entry_price']:.2f} | SL: {signal['stop_loss']:.2f} | TP: {signal['take_profit']:.2f}")
    else:
        print("❌ No signals generated under the current parameters and data conditions.")
```