import streamlit as st
import pandas as pd
import ccxt

st.title("Crypto Scanner - Live Data")

exchange = ccxt.coinex()

# 300 عملة (نبدأ بأشهر أزواج USDT)
symbols = [
    "BTC/USDT", "ETH/USDT", "XRP/USDT", "ADA/USDT", "DOGE/USDT"
]

data = []

for symbol in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=50)
        closes = [candle[4] for candle in ohlcv]

        last_price = closes[-1]

        data.append({
            "Coin": symbol,
            "Price": last_price
        })
    except:
        continue

df = pd.DataFrame(data)
st.dataframe(df)
