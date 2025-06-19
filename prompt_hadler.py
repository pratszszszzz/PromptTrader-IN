import re
from broker import get_quantity, place_order
from symbol_utils import get_symbol_token

def handle_prompt(text):
    action_match = re.search(r"(close|sell|exit|buy)", text, re.IGNORECASE)
    percent_match = re.search(r"(\d+)%", text)
    symbol_match = re.search(r"in ([A-Z]+)", text)

    action = action_match.group(1).lower() if action_match else None
    percent = int(percent_match.group(1)) if percent_match else None
    symbol = symbol_match.group(1) if symbol_match else None

    if not symbol:
        return "Couldn't find the stock symbol in your message."

    symbol_token = get_symbol_token(symbol)
    if not symbol_token:
        return f"Invalid or unsupported symbol: {symbol}"

    if action == "close" and percent:
        qty = get_quantity(symbol)
        if qty > 0:
            sell_qty = max(1, (qty * percent) // 100)
            return place_order(symbol, symbol_token, sell_qty, "SELL")
        else:
            return f"You don't hold any position in {symbol}."

    if action == "buy" and percent:
        qty = percent  
        return place_order(symbol, symbol_token, qty, "BUY")

    return "Sorry, I couldn't understand your request. Try something like: 'Close 50% of my position in TCS'"