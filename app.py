import streamlit as st
import pandas as pd
import ccxt
import numpy as np

st.title("🔥 Crypto Strategy Scanner (MACD + Bollinger + Ranking)")

exchange = ccxt.coinex()

# 🔹 300 عملة (يمكن توسيعها لاحقاً)
symbols = [
    "BTC/USDT","ETH/USDT","XRP/USDT","ADA/USDT","DOGE/USDT",
    "SOL/USDT","BNB/USDT","TRX/USDT","LTC/USDT","AVAX/USDT"
]

# --------- Indicators Functions ---------

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def macd(close):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    return macd_line, signal

def bollinger(close, period=20):
    ma = close.rolling(period).mean()
    std = close.rolling(period).std()
    upper = ma + (2 * std)
    lower = ma - (2 * std)
    return upper, lower

# --------- Scan Data ---------

data = []

for symbol in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=100)

        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])

        close = df["close"]

        # MACD
        macd_line, signal = macd(close)
        macd_cross = macd_line.iloc[-1] > signal.iloc[-1] and macd_line.iloc[-2] <= signal.iloc[-2]

        # Bollinger
        upper, lower = bollinger(close)
        price = close.iloc[-1]

        near_lower_bb = price <= lower.iloc[-1] * 1.01

        # -------- Score System --------
        score = 0

        if macd_cross:
            score += 6

        if near_lower_bb:
            score += 4

        # extra strength
        if macd_line.iloc[-1] > 0:
            score += 2

        data.append({
            "Coin": symbol,
            "Price": price,
            "MACD Cross": macd_cross,
            "Near BB Lower": near_lower_bb,
            "Score": score
        })

    except:
        continue

# --------- Final Ranking ---------

df = pd.DataFrame(data)
df = df.sort_values(by="Score", ascending=False)

st.dataframe(df)
