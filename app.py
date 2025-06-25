import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp  # Make sure pyotp is included in requirements.txt

# Set up Streamlit page
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

# Function for Angel One login using MPIN and TOTP
@st.cache_resource
def angel_login():
    try:
        obj = SmartConnect(api_key=st.secrets["API_KEY"])

        # Generate TOTP dynamically
        totp = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()

        # Perform login with Client ID, MPIN, and TOTP
        session = obj.generateSession(
            st.secrets["CLIENT_ID"],
            st.secrets["MPIN"],
            totp
        )

        feed_token = obj.getfeedToken()
        return obj, feed_token
    except Exception as e:
        st.error(f"Angel login failed. Check credentials or session object.\n\n{e}")
        return None, None

# Function to fetch live option chain data dynamically
@st.cache_data(ttl=30)
def get_live_option_chain():
    smart_api, feed_token = angel_login()
    if not smart_api or not feed_token:
        return pd.DataFrame(columns=["Strike Symbol", "LTP"])

    # Define the strike symbols to be searched
    strike_symbols = ["NIFTY24J27600CE", "NIFTY24J27600PE"]

    data = []
    for symbol in strike_symbols:
        try:
            result = smart_api.searchScrip("NFO", symbol)
            if not result:
                raise ValueError("Symbol not found")

            token = result["data"][0]["token"] if isinstance(result["data"], list) else result["data"]["token"]
            ltp_data = smart_api.ltpData(
                exchange="NFO",
                tradingsymbol=symbol,
                symboltoken=token
            )
            ltp = ltp_data["data"]["ltp"]
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
