def calculate_pe_ratio(price, earnings_per_share):
    """Calculates the Price-to-Earnings ratio of an asset."""
    if earnings_per_share <= 0:
        return float('inf')
    return price / earnings_per_share

def assess_valuation(ticker, pe_ratio, industry_average):
    """Determines if an asset is overvalued based on PE."""
    if pe_ratio > industry_average * 1.5:
        return f"{ticker} is significantly OVERVALUED."
    elif pe_ratio < industry_average * 0.8:
        return f"{ticker} is UNDERVALUED. Potential opportunity."
    else:
        return f"{ticker} is FAIRLY VALUED."
