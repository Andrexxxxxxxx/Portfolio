def format_price(price: float) -> str:
    """Format price with thousand separators and two decimals."""
    return f"{price:,.2f}"

def format_percent(value: float) -> str:
    """Format percentage with sign and two decimals."""
    sign = "+" if value > 0 else ""
    return f"{sign}{value:.2f}%"
