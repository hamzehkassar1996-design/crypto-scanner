import streamlit as st
import pandas as pd
import ccxt
import numpy as np

st.title("🔥 Crypto Scanner v2 (MACD + BB + EMA Filter)")

exchange = ccxt.coinex()

symbols = [
    "BTC/USDT","ETH/USDT","XRP/USDT","ADA/USDT","DOGE/USDT",
    "SOL/USDT","BNB/USDT","TRX/USDT","LTC/USDT","AVAX/USDT"
]

# -------- Indicators --------

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
    return upper, lower, ma

# -------- Scan --------

data = []

for symbol in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=200)

        df = pd.DataFrame(ohlcv, columns=["time","open","high","low","close","volume"])
        close = df["close"]
        price = close.iloc[-1]

        # MACD
        macd_line, signal = macd(close)
        macd_strength = macd_line.iloc[-1] - signal.iloc[-1]

        # Bollinger
        upper, lower, bb_ma = bollinger(close)
        bb_position = (price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])

        # EMA 200 (Trend Filter)
        ema200 = ema(close, 200).iloc[-1]
        trend_ok = price > ema200

        # -------- SCORE --------
        score = 0

        # MACD contribution
        score += max(min(macd_strength * 10, 5), 0)

        # Bollinger contribution
        if bb_position < 0.2:
            score += 4
        elif bb_position < 0.4:
            score += 2

        # Trend filter bonus (مهم جداً)
        if trend_ok:
            score += 3
        else:
            score -= 2  # عقوبة لو ضد الترند

        score += 0.5  # توازن بسيط

        data.append({
            "Coin": symbol,
            "Price": price,
            "MACD Strength": round(macd_strength, 4),
            "BB Position": round(bb_position, 3),
            "EMA200 Trend": trend_ok,
            "Score": round(score, 2)
        })

    except:
        continue

df = pd.DataFrame(data)
df = df.sort_values(by="Score", ascending=False)

st.dataframe(df)
