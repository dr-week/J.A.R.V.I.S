class RiskManager:
    """Intercepts and evaluates actions before they are executed."""
    
    def __init__(self, max_portfolio_risk=0.02):
        self.max_portfolio_risk = max_portfolio_risk # e.g., never risk more than 2%

    def evaluate_trade(self, asset, amount, portfolio_value):
        """Calculates if a simulated trade is too risky."""
        risk_percentage = amount / portfolio_value
        if risk_percentage > self.max_portfolio_risk:
            print(f"[RISK MANAGER] REJECTED: Trade on {asset} risks {risk_percentage*100:.2f}% of portfolio (Max allowed: {self.max_portfolio_risk*100:.2f}%).")
            return False
        
        print(f"[RISK MANAGER] APPROVED: Trade on {asset} is within risk limits.")
        return True
