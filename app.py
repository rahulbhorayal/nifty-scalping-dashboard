import streamlit as st
import pandas as pd
from SmartApi.smartConnect import SmartConnect
import pyotp
import requests
import zipfile
import io

# Set up Streamlit page
st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("\U0001F525 Nifty Option Scalping Dashboard")

# Function to log in to Angel One
@st.cache_resource

def angel_login():
    try:
        obj = SmartConnect(api_key=st.secrets["API_KEY"])
        totp = pyotp.TOTP(st.secrets["TOTP_SECRET"]).now()
        session = obj.generateSession(
            st.secrets["CLIENT_ID"],
            st.secrets["MPIN"],
            totp
        )
        feed_token = obj.getfeedToken()
        return obj, feed_token
    except Exception as e:
        st.error(f"Angel login failed.\n\n{e}")
        return None, None

# Function to fetch instrument data and extract live NIFTY option tokens
@st.cache_data

def load_nifty_option_tokens():
    url = "https://margincalculator.angelbroking.com/OpenAPI_File/files/OpenAPIScripMaster.zip"
    response = requests.get(url)
    z = zipfile.ZipFile(io.BytesIO(response.content))
    csv_file = [f for f in z.namelist() if f.endswith(".csv")][0]
    df = pd.read_csv(z.open(csv_file))
    df = df[df["name"] == "NIFTY"]
    df = df[df["exch_seg"] == "NFO"]
    df = df[df["instrumenttype"] == "OPTIDX"]
    latest = df.sort_values("expiry").iloc[:2]  # Get top 2 entries
    return latest[["symbol", "exch_seg", "token"]].to_dict(orient="records")

# Function to fetch live option chain data
def get_live_option_chain():
    smart_api, feed_token = angel_login()
    if not smart_api or not feed_token:
        return pd.DataFrame(columns=["Strike Symbol", "LTP"])

    symbols = load_nifty_option_tokens()
    data = []
    for item in symbols:
        try:
            ltp_data = smart_api.ltpData(
                exchange=item["exch_seg"],
                tradingsymbol=item["symbol"],
                symboltoken=item["token"]
            )
            ltp = ltp_data["data"]["ltp"]
        except:
            ltp = "--"
        data.append({"Strike Symbol": item["symbol"], "LTP": ltp})

    return pd.DataFrame(data)

# Display Option Chain
st.subheader("\U0001F4C8 Live Nifty Option Chain")
option_data = get_live_option_chain()
st.dataframe(option_data, use_container_width=True)

# Footer
st.markdown("**Data updates every ~30 seconds using Angel One SmartAPI**")