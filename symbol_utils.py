# symbol_utils.py
import pandas as pd
import yfinance as yf
import requests
import zipfile
import io
import os
import datetime

INSTRUMENTS_URL = "https://smartapi.angelbroking.com/instruments"
INSTRUMENTS_FILE = "angel_instruments.csv"

# Auto-download Angel One instrument dump if missing or empty
def download_instruments():
    try:
        response = requests.get(INSTRUMENTS_URL)
        if response.ok:
            z = zipfile.ZipFile(io.BytesIO(response.content))
            z.extractall()
            return True
    except Exception:
        pass
    return False

if not os.path.exists(INSTRUMENTS_FILE) or os.path.getsize(INSTRUMENTS_FILE) == 0:
    download_instruments()

try:
    instrument_df = pd.read_csv(INSTRUMENTS_FILE)
except Exception:
    instrument_df = pd.DataFrame()

def get_symbol_token(symbol, segment="EQ", expiry=None, strike=None, opt_type=None):
    try:
        if segment == "EQ":
            info = yf.Ticker(f"{symbol}.NS").info
            if 'symbol' not in info:
                return None
            filtered = instrument_df[
                (instrument_df['tradingsymbol'].str.upper() == symbol.upper()) &
                (instrument_df['segment'] == "NSE")
            ]
        else:
            expiry_fmt = datetime.datetime.strptime(expiry, "%Y-%m-%d").strftime("%d%b%y").upper()
            strike_str = str(int(strike)) if strike else ""
            tsymbol = f"{symbol.upper()}{expiry_fmt}{strike_str}{opt_type.upper()}"
            filtered = instrument_df[
                (instrument_df['tradingsymbol'] == tsymbol) &
                (instrument_df['segment'] == segment)
            ]

        if not filtered.empty:
            return str(filtered.iloc[0]['token'])
        return None
    except Exception:
        return None
