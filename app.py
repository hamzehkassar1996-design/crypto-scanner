import streamlit as st
import pandas as pd
import ccxt
import numpy as np

st.title("🔥 Stable Crypto Scanner (No Volume Filter Version)")

# =========================
# Exchange Setup
# =========================
exchange = ccxt.binance({
    "enableRateLimit": True,
    "timeout": 10000
})

# =========================
# YOUR COIN LIST
# =========================
symbols_raw = """
DOCK, EMC, ISP, CHRP, EFX, SLN, NETVR, CAIR, SMAND, DEGEN, PRQ, OORT, HGPT,
FROKAI, GTAI, NAI, CERE, LIME, NTX, AURORA, AVIVE, DOP, UXLINK, GLM, LIT, ICX,
STX, ARDR, MANA, GAL, LUNA, FTM, AXL, GAC, BLUR, RAD, CYBER, MOBILE, CBAI,
BOBA, BLOCX, ORBR, SYNT, WSDM, NLK, ANYONE, WOOP, SMH, TOMI, STORY, HTR,
ATS, OGN, DEXE, REQ, CVC, HEDERA, COMBO, BICO, SCRT, FLUX, NULS, EDU, MTL,
STEEM, DCR, WRX, ZETA, NMT, GLQ, DEAI, SAVM, ATR, PYUSD, EAI, PRE, NIBI,
AREA, HNT, EVMOS, XPR, TAIKO, XYO, ORBS, MND, MOVE, TON, ARB, BTC, ETH, XRP
"""

allowed = set([s.strip().upper() for s in symbols_raw.split(",") if s.strip()])
symbols = [f"{coin}/USDT" for coin in allowed]

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

        # =========================
        # MACD
        # =========================
        macd_line, signal = macd(close)
        macd_strength = macd_line.iloc[-1] - signal.iloc[-1]

        # =========================
        # Bollinger
        # =========================
        upper, lower = bollinger(close)
        bb_range = upper.iloc[-1] - lower.iloc[-1]
        bb_position = (price - lower.iloc[-1]) / bb_range if bb_range != 0 else 0

        # =========================
        # Trend
        # =========================
        ema200 = ema(close, 200).iloc[-1]
        trend = price > ema200

        # =========================
        # SCORE SYSTEM (NO VOLUME FILTER)
        # =========================

        score = 0

        # MACD strength
        score += max(min(macd_strength * 10, 5), 0)

        # Bollinger relaxed
        if bb_position < 0.4:
            score += 4
        elif bb_position < 0.7:
            score += 2

        # Trend
        if trend:
            score += 2.5
        else:
            score -= 1.5

        # small stability bonus
        score += 0.5

        # =========================
        # SIGNAL TYPE
        # =========================

        if score >= 7:
            signal_type = "🔥 STRONG BUY"
        elif score >= 4:
            signal_type = "👀 WATCH"
        else:
            signal_type = "❌ WEAK"

        data.append({
            "Coin": symbol,
            "Price": price,
            "Score": round(score, 2),
            "Signal": signal_type
        })

    except:
        continue

# =========================
# OUTPUT
# =========================

df = pd.DataFrame(data)

if df.empty:
    st.warning("⚠️ No signals available right now.")
else:
    df = df[df["Score"] > -1]
    df = df.sort_values(by="Score", ascending=False)

    st.subheader("🔥 Top Opportunities (No Volume Filter)")
    st.dataframe(df.head(20))
