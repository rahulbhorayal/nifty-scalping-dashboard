import streamlit as st
import pandas as pd
from SmartApi import SmartConnect
import pyotp

# Set up the page
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

# Login function using secrets and SmartAPI
@st.cache_resource
def angel_login():
    try:
        api_key = st.secrets["API_KEY"]
        client_id = st.secrets["CLIENT_ID"]
        pwd = st.secrets["PASSWORD"]
        totp = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()

        smartApi = SmartConnect(api_key=api_key)
        session = smartApi.generateSession(client_id, pwd, totp)

        if not session or "data" not in session:
            raise ValueError("Login failed. Check credentials or session response.")

        feed_token = session["data"].get("feedToken") or session["data"].get("feed_token")

        if not feed_token:
            raise ValueError("❌ 'feedToken' missing in session response.")

        return smartApi, feed_token

    except Exception as e:
        st.error(f"Login Failed: {e}")
        return None, None

# Run login
smartApi, feedToken = angel_login()

# Define a few Nifty option strike symbols to track
option_symbols = [
    "NSE:NIFTY2470417800CE",
    "NSE:NIFTY2470418000CE",
    "NSE:NIFTY2470418200CE",
    "NSE:NIFTY2470417800PE",
    "NSE:NIFTY2470418000PE"
]

st.subheader("Live Nifty Option Chain")
placeholder = st.empty()

# Function to fetch latest LTPs
@st.cache_data(ttl=30)
def fetch_ltp(symbol):
    try:
        exchange = symbol.split(":")[0]
        token = symbol.split(":")[1]
        ltp_data = smartApi.ltpData(exchange, token[:-2], token)
        return ltp_data['data']['ltp']
    except:
        return "--"

# Main live update loop
data = []
for sym in option_symbols:
    data.append({
        "Strike Symbol": sym,
        "LTP": fetch_ltp(sym)
    })

# Display live data
df = pd.DataFrame(data)
placeholder.dataframe(df, use_container_width=True)

st.caption("Data updates every ~30 seconds using Angel One SmartAPI")
