def metadata():
    return {"candidate_id": "CAND-B-002", "version": "v2.1.3"}

def parameter_schema():
    return {"lookback_period": 7, "breakout_buffer": 0.1, "trailing_atr_multiplier": 2.0}

def prepare(history):
    if len(history) < 20: return []
    prepared = []
    for i in range(len(history)):
        r = history[i]['High'] - history[i]['Low']
        tr = 0
        if i > 0:
            tr = max(history[i]['High'] - history[i]['Low'], abs(history[i]['High'] - history[i-1]['Close']), abs(history[i]['Low'] - history[i-1]['Close']))
        prepared.append({'range': r, 'tr': tr})
    return prepared

def signal(history, prepared, params):
    n = params['lookback_period']
    if len(history) < n + 1: return 0
    
    curr_idx = len(history) - 1
    curr_range = prepared[curr_idx]['range']
    
    is_nr = True
    sum_range = 0
    for i in range(1, n + 1):
        prev_range = prepared[curr_idx - i]['range']
        if curr_range >= prev_range:
            is_nr = False
            break
        sum_range += prev_range
    
    if not is_nr: return 0
    
    avg_range = sum_range / n
    if curr_range <= avg_range: return 0
    
    atr = sum(p['tr'] for p in prepared[curr_idx-13:curr_idx+1]) / 14
    buffer = params['breakout_buffer']
    
    if history[curr_idx]['Close'] > history[curr_idx]['High'] + buffer:
        return 1
    elif history[curr_idx]['Close'] < history[curr_idx]['Low'] - buffer:
        return -1
    return 0