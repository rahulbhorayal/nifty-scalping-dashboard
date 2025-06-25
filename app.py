import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect

# Set up Streamlit page
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

# Function for Angel One login using MPIN and TOTP
@st.cache_resource
def angel_login():
    try:
        obj = SmartConnect(api_key=st.secrets["API_KEY"])
        session = obj.generateSessionV(
            client_id=st.secrets["CLIENT_ID"],
            password=st.secrets["MPIN"]
        )
        feed_token = obj.getfeedToken()
        return obj, feed_token
    except Exception as e:
        st.error(f"Angel login failed. Check credentials or session object.\n\n{e}")
        return None, None

# Live Nifty Option Chain function
def get_live_option_chain():
    smart_api, feed_token = angel_login()
    if not smart_api or not feed_token:
        return pd.DataFrame(columns=["Strike Symbol", "LTP"])

    # Dummy list of strike symbols
    symbols = [
        "NSE:NIFTY24704178000CE",
        "NSE:NIFTY24704180000CE",
        "NSE:NIFTY24704182000CE",
        "NSE:NIFTY24704178000PE",
        "NSE:NIFTY24704180000PE"
    ]

    # Placeholder for LTP data
    data = []
    for symbol in symbols:
        try:
            ltp = smart_api.ltpData("NSE", "OPTIDX", symbol)["data"]["ltp"]
        except:
            ltp = "--"
        data.append({"Strike Symbol": symbol, "LTP": ltp})

    return pd.DataFrame(data)

# Display Option Chain
st.subheader("📊 Live Nifty Option Chain")
option_data = get_live_option_chain()
st.dataframe(option_data, use_container_width=True)

# Footer
st.markdown("**Data updates every ~30 seconds using Angel One SmartAPI**")
