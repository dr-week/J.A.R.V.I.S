import math

def calculate_expected_value(probability_win, win_amount, probability_loss, loss_amount):
    """
    Calculates the Expected Value (EV) of a scenario.
    EV = (P(Win) * Win_Amount) - (P(Loss) * Loss_Amount)
    """
    ev = (probability_win * win_amount) - (probability_loss * loss_amount)
    return ev

def calculate_volatility(prices):
    """Calculates basic historical volatility (standard deviation of returns)."""
    if len(prices) < 2:
        return 0
    
    returns = []
    for i in range(1, len(prices)):
        ret = (prices[i] - prices[i-1]) / prices[i-1]
        returns.append(ret)
        
    mean_return = sum(returns) / len(returns)
    variance = sum((r - mean_return) ** 2 for r in returns) / len(returns)
    return math.sqrt(variance)
