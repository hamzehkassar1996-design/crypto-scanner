import streamlit as st
import pandas as pd
import ccxt
import numpy as np

st.title("🔥 Advanced Crypto Scanner (Custom Universe + Ranking)")

exchange = ccxt.coinex()

# =========================
# 🟢 YOUR FULL LIST (RAW)
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

# تحويل إلى USDT pairs
symbols = [s.strip().upper() + "/USDT" for s in symbols_raw.split(",")]

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
# Scan Engine
# =========================

data = []

for symbol in symbols:
    try:
        ohlcv = exchange.fetch_ohlcv(symbol, timeframe='15m', limit=120)

        if not ohlcv or len(ohlcv) < 50:
            continue

        df = pd.DataFrame(ohlcv, columns=["t","o","h","l","c","v"])
        close = df["c"]
        price = close.iloc[-1]

        # MACD
        macd_line, signal = macd(close)
        macd_strength = macd_line.iloc[-1] - signal.iloc[-1]

        # Bollinger
        upper, lower = bollinger(close)
        bb_position = (price - lower.iloc[-1]) / (upper.iloc[-1] - lower.iloc[-1])

        # EMA trend filter
        ema200 = ema(close, 200).iloc[-1]
        trend = price > ema200

        # =========================
        # SCORE SYSTEM
        # =========================
        score = 0

        # MACD
        score += max(min(macd_strength * 10, 5), 0)

        # Bollinger
        if bb_position < 0.2:
            score += 4
        elif bb_position < 0.4:
            score += 2

        # Trend filter
        if trend:
            score += 3
        else:
            score -= 2

        # Stability bonus
        score += 0.5

        data.append({
            "Coin": symbol,
            "Price": price,
            "Score": round(score, 2),
            "Trend": trend
        })

    except:
        continue

# =========================
# Final Output
# =========================

df = pd.DataFrame(data)
df = df.sort_values(by="Score", ascending=False)

st.dataframe(df)
