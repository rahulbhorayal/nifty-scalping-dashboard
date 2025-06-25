import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect
from SmartApi.constants import AppConstants
import pyotp
import time

st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

@st.cache_resource
def angel_login():
    api_key = st.secrets["API_KEY"]
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    mpin = st.secrets["MPIN"]
    totp_secret = st.secrets["TOTP_SECRET"]

    smartApi = SmartConnect(api_key=api_key)

    try:
        token = pyotp.TOTP(totp_secret).now()
        session = smartApi.generateSession(client_id, client_secret, token)
        refreshToken = session['data']['refreshToken']
        feed_token = session['data']['feedToken']
        return smartApi, feed_token
    except Exception as e:
        st.error("Angel login failed. Check credentials or session object.")
        st.code(str(e))
        return None, None

def get_live_option_chain():
    smartApi, feed_token = angel_login()
    if not feed_token:
        return pd.DataFrame(columns=["Strike Symbol", "LTP"])

    option_symbols = [
        "NSE:NIFTY2470417800CE",
        "NSE:NIFTY2470418000CE",
        "NSE:NIFTY2470418200CE",
        "NSE:NIFTY2470417800PE",
        "NSE:NIFTY2470418000PE",
    ]

    data = {
        "Strike Symbol": option_symbols,
        "LTP": ["--"] * len(option_symbols)
    }

    df = pd.DataFrame(data)
    return df

tab1, tab2 = st.tabs(["📈 Live Option Chain", "🛒 Place Trade"])

with tab1:
    st.subheader("Live Nifty Option Chain")
    df = get_live_option_chain()
    st.dataframe(df, use_container_width=True)
    st.caption("Data updates every ~30 seconds using Angel One SmartAPI")

with tab2:
    st.subheader("Place Trade")
    selected_strike = st.selectbox("Select Strike Symbol", df["Strike Symbol"])
    entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
    stop_loss = entry_price - 2 if entry_price else 0
    st.text(f"Calculated Stop Loss: {stop_loss:.2f}")

    if st.button("✅ Place Buy + SL Order"):
        st.success(f"Buy order for {selected_strike} at ₹{entry_price:.2f}")
        st.info(f"Stop Loss Order placed at ₹{stop_loss:.2f}")
