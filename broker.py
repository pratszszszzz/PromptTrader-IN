from smartapi.smartConnect import SmartConnect
from symbol_utils import get_symbol_token
from lot_size import get_lot_size
import os

API_KEY = os.getenv("ANGEL_API_KEY")
CLIENT_CODE = os.getenv("ANGEL_CLIENT_CODE")
PASSWORD = os.getenv("ANGEL_PASSWORD")
TOTP = os.getenv("ANGEL_TOTP")

obj = SmartConnect(api_key=API_KEY)
session = obj.generateSession(CLIENT_CODE, PASSWORD, TOTP)

def place_order(parsed_prompt):
    strategy = parsed_prompt.get("strategy")

    if strategy in ["long_straddle", "short_straddle"]:
        return execute_straddle(parsed_prompt)

    symbol = parsed_prompt["symbol"]
    segment = parsed_prompt["segment"]
    expiry = parsed_prompt.get("expiry")
    strike = parsed_prompt.get("strike")
    opt_type = parsed_prompt.get("opt_type")

    token = get_symbol_token(symbol, segment, expiry, strike, opt_type)
    if not token:
        return f"Symbol token not found for {symbol}"

    action = parsed_prompt["action"]
    ordertype = "MARKET"
    tradingsymbol = symbol

    if segment != "EQ":
        expiry_fmt = expiry.split("-")[2][2:] + expiry.split("-")[1].upper() + expiry.split("-")[0]
        tradingsymbol = f"{symbol.upper()}{expiry_fmt}{int(strike)}{opt_type.upper()}"

    if parsed_prompt["lots"]:
        lot_size = get_lot_size(symbol)
        if not lot_size:
            return f"Lot size not found for {symbol}"
        quantity = parsed_prompt["lots"] * lot_size
    elif parsed_prompt["qty"]:
        quantity = parsed_prompt["qty"]
    else:
        return "No quantity specified"

    transaction_type = "BUY" if action == "buy" else "SELL"

    try:
        orderparams = {
            "variety": "NORMAL",
            "tradingsymbol": tradingsymbol,
            "symboltoken": token,
            "transactiontype": transaction_type,
            "exchange": "NSE" if segment == "EQ" else "NFO",
            "ordertype": ordertype,
            "producttype": "INTRADAY",
            "duration": "DAY",
            "price": "0",
            "squareoff": "0",
            "stoploss": "0",
            "quantity": quantity
        }
        orderId = obj.placeOrder(orderparams)
        return f"✅ Order placed. ID: {orderId}"
    except Exception as e:
        return f"❌ Failed to place order: {str(e)}"

def execute_straddle(parsed):
    symbol = parsed["symbol"]
    expiry = parsed["expiry"]
    strike = parsed["strike"]
    lots = parsed["lots"]
    action = "BUY" if parsed["strategy"] == "long_straddle" else "SELL"
    segment = "OPTIDX"

    lot_size = get_lot_size(symbol)
    if not lot_size:
        return f"Lot size not found for {symbol}"

    expiry_fmt = expiry.split("-")[2][2:] + expiry.split("-")[1].upper() + expiry.split("-")[0]
    results = []

    for opt in ["CE", "PE"]:
        tradingsymbol = f"{symbol.upper()}{expiry_fmt}{int(strike)}{opt}"
        token = get_symbol_token(symbol, segment, expiry, strike, opt)
        if not token:
            results.append(f"Token not found for {opt}")
            continue

        try:
            orderparams = {
                "variety": "NORMAL",
                "tradingsymbol": tradingsymbol,
                "symboltoken": token,
                "transactiontype": action,
                "exchange": "NFO",
                "ordertype": "MARKET",
                "producttype": "INTRADAY",
                "duration": "DAY",
                "price": "0",
                "squareoff": "0",
                "stoploss": "0",
                "quantity": lots * lot_size
            }
            order_id = obj.placeOrder(orderparams)
            results.append(f"✅ {opt} order placed. ID: {order_id}")
        except Exception as e:
            results.append(f"❌ {opt} order failed: {str(e)}")

    return "\n".join(results)
