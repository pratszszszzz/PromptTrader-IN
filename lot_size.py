lot_sizes = {
    "NIFTY": 50,
    "BANKNIFTY": 15,
    "FINNIFTY": 40,
    "MIDCPNIFTY": 75,
    "SENSEX": 10,
    "RELIANCE": 505,
    "SBIN": 1500
}

def get_lot_size(symbol):
    return lot_sizes.get(symbol.upper(), None)