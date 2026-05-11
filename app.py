import streamlit as st
import pandas as pd

st.title("Crypto Scanner (First Version)")

# بيانات تجريبية الآن فقط
data = {
    "Coin": ["BTC", "ETH", "XRP", "ADA"],
    "MACD": [1, -1, 2, 0.5],
    "Bollinger": ["Low", "Low", "Mid", "High"],
    "Score": [8, 5, 9, 4]
}

df = pd.DataFrame(data)

df = df.sort_values(by="Score", ascending=False)

st.dataframe(df)
