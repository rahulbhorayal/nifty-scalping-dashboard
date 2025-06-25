import streamlit as st
import pandas as pd
import threading
from SmartApi.smartConnect import SmartConnect
from SmartApi.smartWebSocketV2 import SmartWebSocketV2
import pyotp
import json

st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

# Login and generate tokens
@st.cache_resource
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

# Get token using SmartAPI's searchScrip
def get_token(api, symbol, exchange):
    try:
        res = api.searchScrip(exchange=exchange, symbol=symbol)
        return res['data'][0]['token']
    except:
        return None

# Store live LTPs in session
if "live_ltp" not in st.session_state:
    st.session_state.live_ltp = {}

symbols = [("NIFTY24J27600CE", "NFO"), ("NIFTY24J27600PE", "NFO")]

api, feed_token, client_code = angel_login()
symbol_tokens = []

for sym, exch in symbols:
    token = get_token(api, sym, exch)
    if token:
        symbol_tokens.append({
            "symbol": sym,
            "token": token,
            "exchange": exch,
        })

# WebSocket setup
def on_tick(wsapp, message):
    print("✅ Tick received:", message)  # <-- Add this line
    data = json.loads(message)
    for item in data['data']:
        sym = item['tsym']
        ltp = item['ltp']
        st.session_state.live_ltp[sym] = ltp

def on_open(wsapp):
    print("🚀 WebSocket opened")  # <-- Add this line
    tokens = [{"exch": "NFO", "token": s["token"]} for s in symbol_tokens]
    print("📡 Subscribing to tokens:", tokens)  # <-- Add this line
    wsapp.subscribe(tokens)

# Run WebSocket in background
def run_websocket():
    ws = SmartWebSocketV2(
        feedToken=feed_token,
        client_code=client_code,
        api_key=st.secrets["API_KEY"]
    )
    ws.on_open = on_open
    ws.on_tick = on_tick
    ws.connect()

if "ws_thread_started" not in st.session_state:
    thread = threading.Thread(target=run_websocket)
    thread.start()
    st.session_state.ws_thread_started = True

# Show real-time data
st.subheader("📊 Live Nifty Option Chain")
table = []
for s in symbol_tokens:
    sym = s["symbol"]
    ltp = st.session_state.live_ltp.get(sym, "--")
    table.append({"Strike Symbol": sym, "LTP": ltp})

st.dataframe(pd.DataFrame(table), use_container_width=True)
