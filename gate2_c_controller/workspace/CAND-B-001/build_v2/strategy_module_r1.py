def metadata():
    return {"candidate_id": "CAND-B-001", "version": "v2.1.1"}

def parameter_schema():
    return {"atr_period": 14, "body_multiplier": 1.5, "risk_reward_ratio": 2.0}

def prepare(history):
    if len(history) < 30: return None
    closes = [h['Close'] for h in history]
    opens = [h['Open'] for h in history]
    highs = [h['High'] for h in history]
    lows = [h['Low'] for h in history]
    
    tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(history))]
    atr = sum(tr[-14:]) / 14
    atr_ma = sum([sum([max(highs[j] - lows[j], abs(highs[j] - closes[j-1]), abs(lows[j] - closes[j-1])) for j in range(i-14, i)])/14 for i in range(len(history)-20, len(history))]) / 20
    
    body_sizes = [abs(closes[i] - opens[i]) for i in range(len(history)-10, len(history))]
    avg_body = sum(body_sizes) / 10
    
    return {"atr": atr, "atr_ma": atr_ma, "avg_body": avg_body}

def signal(history, prepared, params):
    if not prepared or len(history) < 2: return 0
    
    curr = history[-1]
    prev = history[-2]
    
    # Regime Filter
    if prepared['atr'] >= prepared['atr_ma']: return 0
    
    body = abs(curr['Close'] - curr['Open'])
    range_val = curr['High'] - curr['Low']
    if range_val == 0: return 0
    
    is_exhaustion = (body / range_val < 0.2) and (body > params['body_multiplier'] * prepared['avg_body'])
    
    if is_exhaustion:
        # Bullish exhaustion: Bearish signal
        if curr['Close'] > curr['Open']:
            if prev['Close'] < curr['Low']: return -1
        # Bearish exhaustion: Bullish signal
        elif curr['Close'] < curr['Open']:
            if prev['Close'] > curr['High']: return 1
            
    return 0