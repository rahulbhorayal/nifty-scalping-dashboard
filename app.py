import streamlit as st
import pandas as pd
import pyotp
from SmartApi.smartConnect import SmartConnect
import time

# -------------------------------
# 🧠 Your Angel One API Details
# -------------------------------
API_KEY = "EnOXc5bE"
CLIENT_CODE = "AAAN045886"
PASSWORD = "Rahul@1milliondollar"
TOTP_SECRET = "7CXNCG54UO5ZYS7RXNFVTMRNGA"

# -------------------------------
# 🧾 Get Access Token using TOTP
# -------------------------------
@st.cache_resource(show_spinner=False)
def angel_login():
    smartApi = SmartConnect(api_key=API_KEY)
    token = pyotp.TOTP(TOTP_SECRET).now()
    session = smartApi.generateSession(CLIENT_CODE, PASSWORD, token)
    return smartApi, session["feedToken"]

# -------------------------------
# 🟢 Simulated Live Option Data (replace later with WebSocket)
# -------------------------------
def get_live_option_chain():
    # This part will later be replaced by actual WebSocket price updates
    return pd.DataFrame({
        'Strike Symbol': [
            'NIFTY2452717900CE', 'NIFTY2452718000CE',
            'NIFTY2452718100CE', 'NIFTY2452717900PE',
            'NIFTY2452718000PE', 'NIFTY2452718100PE'
        ],
        'LTP': [118.6, 120.2, 122.1, 111.45, 109.9, 108.4]
    })

# -------------------------------
# 📊 Streamlit UI
# -------------------------------
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("⚡ Nifty Option Scalping Dashboard")

tab1, tab2 = st.tabs(["Live Option Chain", "Place Trade"])

with tab1:
    st.subheader("Live Nifty Option Chain")

    # Authenticate
    with st.spinner("Logging in to Angel One..."):
        smartApi, feedToken = angel_login()
        st.success("Logged in successfully!")

    # Show mock data (replace with real-time later)
    df = get_live_option_chain()
    st.dataframe(df, use_container_width=True)

with tab2:
    st.subheader("Place Trade (Simulated)")
    selected_strike = st.selectbox("Select Strike", df['Strike Symbol'])
    entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
    stop_loss = entry_price - 1 if entry_price else 0
    st.text(f"Calculated Stop Loss: ₹{stop_loss:.2f}")

    if st.button("📈 Place Buy + SL Order"):
        st.success(f"Simulated Buy Order: {selected_strike} at ₹{entry_price:.2f}")
        st.info(f"Stop Loss set at ₹{stop_loss:.2f}")
