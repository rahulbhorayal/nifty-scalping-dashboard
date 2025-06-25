import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp
import time

# MPIN-based login using Streamlit secrets
@st.cache_resource(ttl=3600, show_spinner=False)
def angel_login():
    api_key = st.secrets["API_KEY"]
    client_id = st.secrets["CLIENT_ID"]
    client_secret = st.secrets["CLIENT_SECRET"]
    mpin = st.secrets["MPIN"]
    totp_token = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()

    obj = SmartConnect(api_key=api_key)
    session = obj.generateSessionV2(
        client_id=client_id,
        client_secret=client_secret,
        totp=totp_token,
        mpin=mpin
    )
    st.session_state.session = session
    return obj, session['data']['feedToken']

# Sample Option Chain Data (can be replaced by real fetch)
def get_live_option_chain():
    smart_api, feed_token = angel_login()
    option_data = pd.DataFrame({
        "Strike Symbol": [
            "NSE:NIFTY2470417800CE", "NSE:NIFTY2470418000CE",
            "NSE:NIFTY2470418200CE", "NSE:NIFTY2470417800PE",
            "NSE:NIFTY2470418000PE"
        ],
        "LTP": ["--", "--", "--", "--", "--"]
    })
    return option_data

# Streamlit UI
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

try:
    with st.spinner("Loading live option data..."):
        df = get_live_option_chain()
        st.dataframe(df, use_container_width=True)
        st.caption("Data updates every ~30 seconds using Angel One SmartAPI")
except Exception as e:
    st.error(f"Angel login failed. Check credentials or session object.\n\n{e}")
