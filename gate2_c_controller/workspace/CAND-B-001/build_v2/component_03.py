```python
def calculate_risk_parameters(entry_price, atr_value, atr_multiplier=2.0, risk_reward_ratio=2.0):
    """
    Calculates Stop Loss and Take Profit levels based on ATR volatility.
    
    :param entry_price: The price at which the position is opened.
    :param atr_value: The current Average True Range value.
    :param atr_multiplier: Multiplier for the ATR to determine the stop distance.
    :param risk_reward_ratio: The desired ratio of profit to risk.
    :return: Dictionary containing 'stop_loss' and 'take_profit' levels.
    """
    
    # Calculate the risk amount based on ATR
    risk_amount = atr_value * atr_multiplier
    
    # Calculate the reward amount based on the risk-reward ratio
    reward_amount = risk_amount * risk_reward_ratio
    
    # Assuming a Long position
    stop_loss = entry_price - risk_amount
    take_profit = entry_price + reward_amount
    
    return {
        "entry_price": entry_price,
        "stop_loss": round(stop_loss, 4),
        "take_profit": round(take_profit, 4),
        "risk_amount": round(risk_amount, 4),
        "reward_amount": round(reward_amount, 4)
    }

# Example Usage:
if __name__ == "__main__":
    entry = 150.00
    atr = 1.50
    
    params = calculate_risk_parameters(entry, atr)
    print(f"Entry: {params['entry_price']}")
    print(f"Stop Loss: {params['stop_loss']}")
    print(f"Take Profit: {params['take_profit']}")
```