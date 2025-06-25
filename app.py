import streamlit as st
import pandas as pd
import threading
from SmartApi.smartConnect import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import json

st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

st.write("🟢 Starting simplified test")

def angel_login():
    obj = SmartConnect(api_key=st.secrets["API_KEY"])
    totp = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()
    session = obj.generateSession(
        st.secrets["CLIENT_ID"],
        st.secrets["MPIN"],
        totp
    )
    feed_token = obj.getfeedToken()
    return obj, feed_token, st.secrets["CLIENT_ID"]

def get_token(api, symbol, exchange):
    try:
        res = api.searchScrip(exchange=exchange, symbol=symbol)
        return res['data'][0]['token']
    except:
        return None

api, feed_token, client_code = angel_login()
print("🟢 Login success:", api is not None, "| feed_token:", feed_token)

symbols = [("NIFTY24J27600CE", "NFO"), ("NIFTY24J27600PE", "NFO")]
print("📦 Symbols list to fetch:", symbols)

symbol_tokens = []

for sym, exch in symbols:
    token = get_token(api, sym, exch)
    print(f"Symbol: {sym}, Token: {token}")
    if token:
        symbol_tokens.append({
            "symbol": sym,
            "token": token,
            "exchange": exch,
        })

st.write("✅ Token debug result")
st.write(symbol_tokens)
