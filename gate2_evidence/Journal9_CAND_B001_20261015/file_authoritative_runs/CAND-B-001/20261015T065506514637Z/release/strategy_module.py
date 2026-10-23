import pandas as pd
import numpy as np

def metadata():
    return {
        "candidate_id": "CAND-B-001",
        "version": "v2.1.1",
        "research_domain": "XAUUSD M1 Price Action"
    }

def parameter_schema():
    return {
        "atr_period": 14,
        "body_multiplier": 1.5,
        "risk_reward_ratio": 2.0
    }

def prepare(history):
    if len(history) < 30:
        return None
    df = pd.DataFrame(history)
    body = (df['close'] - df['open']).abs()
    candle_range = (df['high'] - df['low']).replace(0, 1e-9)
    df['body_ratio'] = body / candle_range
    df['avg_body'] = body.rolling(10).mean()
    df['rel_body'] = body / df['avg_body']
    df['atr_ma'] = df['atr'].rolling(20).mean()
    df['is_low_vol'] = (df['atr'] < df['atr_ma']).astype(int)
    return df

def signal(history, prepared, params):
    if prepared is None or len(prepared) < 2:
        return 0
    
    curr = prepared.iloc[-1]
    prev = prepared.iloc[-2]
    
    # Regime Filter
    if curr['is_low_vol'] == 0:
        return 0
    
    # Exhaustion Logic
    # Bullish: (Open - Close) / Range < 0.2, Body > 1.5 * Avg
    is_bullish_exhaustion = ((prev['open'] - prev['close']) / (prev['high'] - prev['low']) < 0.2) and \
                            (prev['open'] > prev['close']) and \
                            (abs(prev['close'] - prev['open']) > params['body_multiplier'] * prev['avg_body'])
    
    # Bearish: (Close - Open) / Range < 0.2, Body > 1.5 * Avg
    is_bearish_exhaustion = ((prev['close'] - prev['open']) / (prev['high'] - prev['low']) < 0.2) and \
                            (prev['close'] > prev['open']) and \
                            (abs(prev['close'] - prev['open']) > params['body_multiplier'] * prev['avg_body'])
    
    # Entry Triggers
    if is_bullish_exhaustion and curr['close'] < prev['low']:
        return -1 # Short
    if is_bearish_exhaustion and curr['close'] > prev['high']:
        return 1  # Long
        
    return 0