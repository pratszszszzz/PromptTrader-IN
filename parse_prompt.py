import re
import datetime

def parse_trade_prompt(prompt):
    prompt = prompt.lower()
    result = {
        "action": None,
        "symbol": None,
        "percent": None,
        "qty": None,
        "segment": "EQ",
        "expiry": None,
        "strike": None,
        "opt_type": None,
        "lots": None,
        "strategy": None  
    }

    if "long straddle" in prompt:
        result["strategy"] = "long_straddle"
        result["action"] = "buy"
        result["segment"] = "OPTIDX"
        result["symbol"] = "NIFTY"  # defaulting to NIFTY
    elif "short straddle" in prompt:
        result["strategy"] = "short_straddle"
        result["action"] = "sell"
        result["segment"] = "OPTIDX"
        result["symbol"] = "NIFTY"

    percent_match = re.search(r"(\d+)%", prompt)
    if percent_match:
        result["percent"] = int(percent_match.group(1))

    lot_match = re.search(r"(\d+)\s+lot", prompt)
    if lot_match:
        result["lots"] = int(lot_match.group(1))
    else:
        result["lots"] = 1 if result["strategy"] else None

    strike_match = re.search(r"strike\s+(\d+)", prompt)
    if strike_match:
        result["strike"] = int(strike_match.group(1))

    expiry_match = re.search(r"expiry\s+(\d{1,2})\s+([a-zA-Z]{3})", prompt)
    if expiry_match:
        try:
            day = int(expiry_match.group(1))
            month = expiry_match.group(2).upper()
            year = datetime.datetime.now().year
            dt = datetime.datetime.strptime(f"{day} {month} {year}", "%d %b %Y")
            if dt < datetime.datetime.now():
                dt = dt.replace(year=year + 1)
            result["expiry"] = dt.strftime("%Y-%m-%d")
        except:
            pass

    if not result["symbol"]:
        symbol_match = re.search(r"\b([A-Z]{3,10})\b", prompt.upper())
        if symbol_match:
            result["symbol"] = symbol_match.group(1)

    qty_match = re.search(r"buy\s+(\d+)", prompt)
    if qty_match and not result["lots"]:
        result["qty"] = int(qty_match.group(1))

    return result
