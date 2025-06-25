import streamlit as st
import pandas as pd
import requests
from SmartApi.smartConnect import SmartConnect

# Set up Streamlit page
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("🔥 Nifty Option Scalping Dashboard")

# Function to login using MPIN
@st.cache_resource
def angel_login():
    try:
        obj = SmartConnect(api_key=st.secrets["API_KEY"])
        session = obj.generateSession(
            client_id=st.secrets["CLIENT_ID"],
            password=st.secrets["MPIN"]
        )
        feed_token = obj.getfeedToken()
        return obj, feed_token
    except Exception as e:
        st.error(f"Angel login failed. Check credentials or session object.\n\n{e}")
        return None, None

# Function to load instrument list
@st.cache_resource
def load_instruments():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.json"
    instruments = requests.get(url).json()
    df = pd.DataFrame(instruments)
    return df

# Function to get tokens for strike prices
def get_strike_tokens(df, underlying='NIFTY', expiry='25JUL2024', strikes=[17800, 18000, 18200], option_type='CE'):
    result = []
    for strike in strikes:
        row = df[
            (df['name'] == underlying) &
            (df['expiry'] == expiry) &
            (df['strike'] == strike * 100) &
            (df['symbol'].str.endswith(option_type))
        ].head(1)
        if not row.empty:
            result.append({
                "symbol": row.iloc[0]["symbol"],
                "token": row.iloc[0]["token"]
            })
    return result

# Function to get live option chain
def get_live_option_chain():
    smart_api, feed_token = angel_login()
    if not smart_api or not feed_token:
        return pd.DataFrame(columns=["Strike Symbol", "LTP"])

    df = load_instruments()
    symbols = get_strike_tokens(df, expiry='25JUL2024', strikes=[17800, 18000, 18200], option_type='CE') + \
              get_strike_tokens(df, expiry='25JUL2024', strikes=[17800, 18000], option_type='PE')

    data = []
    for item in symbols:
        try:
            ltp = smart_api.ltpData('NFO', item['symbol'], item['token'])['data']['ltp']
        except:
            ltp = "--"
        data.append({"Strike Symbol": item['symbol'], "LTP": ltp})

    return pd.DataFrame(data)

# Display Option Chain
st.subheader("📊 Live Nifty Option Chain")
option_data = get_live_option_chain()
st.dataframe(option_data, use_container_width=True)

# Footer
st.markdown("**Data updates every ~30 seconds using Angel One SmartAPI**")
