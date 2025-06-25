import streamlit as st
import pandas as pd

# Placeholder for live options data (simulate for prototype)
def get_live_option_chain():
    return pd.DataFrame({
        'Strike Symbol': [
            'NIFTY2452717900CE', 'NIFTY2452718000CE', 'NIFTY2452718100CE',
            'NIFTY2452717900PE', 'NIFTY2452718000PE', 'NIFTY2452718100PE'
        ],
        'LTP': [118.6, 120.2, 122.1, 111.45, 109.9, 108.4]
    })

st.set_page_config(page_title="Nifty Option Scalping", layout="wide")
st.title("⚡ Nifty Option Scalping Dashboard")

# Live data simulation
data_load_state = st.text('Loading live option data...')
data = get_live_option_chain()
data_load_state.text('')

# Display data
tab1, tab2 = st.tabs(["Live Option Chain", "Place Trade"])

with tab1:
    st.subheader("Live Nifty Option Chain")
    st.dataframe(data, use_container_width=True)

with tab2:
    st.subheader("Place Trade")
    selected_strike = st.selectbox("Select Strike Symbol", data['Strike Symbol'])
    entry_price = st.number_input("Entry Price", min_value=0.0, format="%.2f")
    stop_loss = entry_price - 1 if entry_price else 0
    st.text(f"Calculated Stop Loss: ₹{stop_loss:.2f}")

    if st.button("📈 Place Buy + SL Order"):
        # In actual version, integrate API call here
        st.success(f"Buy Order for {selected_strike} at ₹{entry_price:.2f} placed.")
        st.info(f"Stop Loss Order placed at ₹{stop_loss:.2f}")
