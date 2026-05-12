import streamlit as st
import pandas as pd
import ccxt

st.title("🔥 Stable Top 10 Scanner (Fixed Symbols)")

exchange = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 10000
})

# =========================
# FIX: Get real Binance USDT pairs
# =========================
try:
    markets = exchange.fetch_tickers()

    all_symbols = [
        s for s in markets.keys()
        if s.endswith("/USDT")
    ]

    # نأخذ أول 50 عملة فقط
    symbols = all_symbols[:50]

except:
    st.error("❌ Failed to load market data")
    st.stop()

# =========================
# Indicators
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

        macd_line, signal = macd(close)
        macd_value = macd_line.iloc[-1] - signal.iloc[-1]

        upper, lower = bollinger(close)
        bb_range = upper.iloc[-1] - lower.iloc[-1]
        bb_position = (price - lower.iloc[-1]) / bb_range if bb_range != 0 else 0

        score = 0

        if macd_value > 0:
            score += 1

        if bb_position < 0.5:
            score += 1

        if score == 2:
            signal_type = "🔥 BUY"
        elif score == 1:
            signal_type = "👀 WATCH"
        else:
            signal_type = "❌ NO SIGNAL"

        data.append({
            "Coin": symbol,
            "Price": price,
            "Score": score,
            "Signal": signal_type
        })

    except:
        continue

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No signals available right now.")
else:
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🔥 Top 10 Opportunities")
    st.dataframe(df.head(10))
