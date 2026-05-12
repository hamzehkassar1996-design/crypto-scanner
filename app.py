import streamlit as st
import pandas as pd
import ccxt
import numpy as np

st.title("🔥 Simple Crypto Scanner (Top 10 | MACD + Bollinger | 15m)")

# =========================
# Exchange
# =========================
exchange = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 10000
})

# =========================
# 50 COINS
# =========================
symbols_raw = """
BTC, ETH, BNB, SOL, XRP, ADA, DOGE, TRX, AVAX,
TON, SHIB, LTC, DOT, BCH, LINK, MATIC, UNI, ATOM,
ETC, NEAR, FIL, APT, ARB, OP, ICP, VET, ALGO,
XLM, HBAR, SAND, MANA, AAVE, EGLD, GRT, THETA,
AXS, QNT, IMX, INJ, RNDR, FTM, CRV, RUNE, KAVA,
GALA, ZEC, COMP, SNX, LDO
"""

allowed = [s.strip().upper() for s in symbols_raw.split(",") if s.strip()]
symbols = [f"{coin}/USDT" for coin in allowed]

# =========================
# INDICATORS
# =========================

def ema(series, period):
    return series.ewm(span=period, adjust=False).mean()

def macd(close):
    ema12 = ema(close, 12)
    ema26 = ema(close, 26)
    macd_line = ema12 - ema26
    signal = ema(macd_line, 9)
    return macd_line, signal

def bollinger(close):
    ma = close.rolling(20).mean()
    std = close.rolling(20).std()
    upper = ma + (2 * std)
    lower = ma - (2 * std)
    return upper, lower

# =========================
# SCANNER
# =========================

data = []

for symbol in symbols:

    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe="15m", limit=120)

        if not ohlcv or len(ohlcv) < 50:
            continue

        df = pd.DataFrame(ohlcv, columns=["t","o","h","l","c","v"])
        close = df["c"]
        price = close.iloc[-1]

        # MACD
        macd_line, signal = macd(close)
        macd_value = macd_line.iloc[-1] - signal.iloc[-1]

        # Bollinger
        upper, lower = bollinger(close)
        bb_range = upper.iloc[-1] - lower.iloc[-1]
        bb_position = (price - lower.iloc[-1]) / bb_range if bb_range != 0 else 0

        # =========================
        # SCORE SYSTEM (SIMPLE)
        # =========================
        score = 0

        if macd_value > 0:
            score += 1

        if bb_position < 0.5:
            score += 1

        # SIGNAL
        if score == 2:
            signal_type = "🔥 BUY"
        elif score == 1:
            signal_type = "👀 WATCH"
        else:
            signal_type = "❌ NO SIGNAL"

        data.append({
            "Coin": symbol,
            "Price": round(price, 6),
            "Score": score,
            "MACD": round(macd_value, 4),
            "BB Position": round(bb_position, 2),
            "Signal": signal_type
        })

    except:
        continue

# =========================
# OUTPUT
# =========================

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No data available right now.")
else:
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🔥 Top 10 Opportunities (Ranked)")
    st.dataframe(df.head(10))
