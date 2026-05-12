import streamlit as st
import pandas as pd
import ccxt

st.title("🔥 Stable Top 10 Scanner (Debug + Safe Mode)")

# =========================
# Exchange Setup (STABLE)
# =========================
exchange = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 30000,
    "options": {
        "defaultType": "spot"
    },
    "headers": {
        "User-Agent": "Mozilla/5.0"
    }
})

# =========================
# TEST CONNECTION (IMPORTANT)
# =========================
try:
    test = exchange.fetch_ohlcv("BTC/USDT", "15m", limit=5)
    st.success("✅ Binance connection OK")
except Exception as e:
    st.error(f"❌ Connection failed: {e}")
    st.stop()

# =========================
# 50 COINS
# =========================
symbols = [
    "BTC/USDT", "ETH/USDT", "BNB/USDT", "SOL/USDT", "XRP/USDT",
    "ADA/USDT", "DOGE/USDT", "TRX/USDT", "AVAX/USDT", "TON/USDT",
    "SHIB/USDT", "LTC/USDT", "DOT/USDT", "BCH/USDT", "LINK/USDT",
    "MATIC/USDT", "UNI/USDT", "ATOM/USDT", "ETC/USDT", "NEAR/USDT",
    "FIL/USDT", "APT/USDT", "ARB/USDT", "OP/USDT", "ICP/USDT",
    "VET/USDT", "ALGO/USDT", "XLM/USDT", "HBAR/USDT", "SAND/USDT",
    "MANA/USDT", "AAVE/USDT", "EGLD/USDT", "GRT/USDT", "THETA/USDT",
    "AXS/USDT", "QNT/USDT", "IMX/USDT", "INJ/USDT", "RNDR/USDT",
    "FTM/USDT", "CRV/USDT", "RUNE/USDT", "KAVA/USDT", "GALA/USDT",
    "ZEC/USDT", "COMP/USDT", "SNX/USDT", "LDO/USDT"
]

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
# SCANNER ENGINE
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
        # SCORE SYSTEM
        # =========================
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
            "MACD": round(macd_value, 4),
            "BB Position": round(bb_position, 2),
            "Signal": signal_type
        })

    except Exception as e:
        st.write(f"Error in {symbol}: {e}")
        continue

# =========================
# OUTPUT
# =========================

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No data available right now.")
else:
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🔥 Top 10 Opportunities")
    st.dataframe(df.head(10))
