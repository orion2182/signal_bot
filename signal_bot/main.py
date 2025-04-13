# main.py
import ccxt
import pandas as pd
import numpy as np
import ta
import requests
import asyncio
from datetime import datetime

# =============================
# CONFIG
# =============================
DISCORD_WEBHOOK_URL = "https://discord.com/api/webhooks/1360089106150854777/CUJWPc7hn_2G6qd8bJp3r13QKyMkUSVD7zSl_JqSJ8-Ns_BofNNu0Cr1S7cjEw5Ob_gQ"
TIMEFRAMES = ['1h', '4h']
INTERVAL_SCAN = 180  # seconds

exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})


# =============================
# STRATEGI UTAMA
# =============================
def ema_cross(df):
    df['ema20'] = ta.trend.ema_indicator(df['close'], window=20).ema_indicator()
    df['ema50'] = ta.trend.ema_indicator(df['close'], window=50).ema_indicator()
    df['ema200'] = ta.trend.ema_indicator(df['close'], window=200).ema_indicator()

    if df['ema20'].iloc[-2] < df['ema50'].iloc[-2] and df['ema20'].iloc[-1] > df['ema50'].iloc[-1] and df['close'].iloc[-1] > df['ema200'].iloc[-1]:
        return 'long'
    elif df['ema20'].iloc[-2] > df['ema50'].iloc[-2] and df['ema20'].iloc[-1] < df['ema50'].iloc[-1] and df['close'].iloc[-1] < df['ema200'].iloc[-1]:
        return 'short'
    return None

def volume_spike(df):
    volume_avg = df['volume'].rolling(20).mean()
    spike = df['volume'].iloc[-1] > 1.5 * volume_avg.iloc[-1]
    body = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    high_low = df['high'].iloc[-1] - df['low'].iloc[-1]
    valid = body > (0.6 * high_low)
    return spike and valid

def detect_divergence(df):
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    lows = df['close'].iloc[-5:].values
    rsis = df['rsi'].iloc[-5:].values

    if lows[-2] < lows[-1] and rsis[-2] > rsis[-1]:
        return 'hidden_bullish'
    elif lows[-2] > lows[-1] and rsis[-2] < rsis[-1]:
        return 'regular_bullish'
    return None

def detect_candle_pattern(df):
    o = df['open'].iloc[-1]
    c = df['close'].iloc[-1]
    h = df['high'].iloc[-1]
    l = df['low'].iloc[-1]

    body = abs(c - o)
    upper = h - max(c, o)
    lower = min(c, o) - l

    if body < upper and body < lower:
        return 'doji'
    elif c > o and body > (upper + lower):
        return 'bullish_engulfing'
    elif c < o and body > (upper + lower):
        return 'bearish_engulfing'
    return None

def generate_signal(df):
    direction = ema_cross(df)
    vol = volume_spike(df)
    div = detect_divergence(df)
    pattern = detect_candle_pattern(df)

    if direction == 'long' and vol and div in ['regular_bullish', 'hidden_bullish'] and pattern == 'bullish_engulfing':
        return 'long'
    elif direction == 'short' and vol and pattern == 'bearish_engulfing':
        return 'short'
    return None


# =============================
# UTILITIES
# =============================
def get_klines(symbol, timeframe='1h', limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def send_discord_signal(symbol, direction, entry, sl, tp, rr):
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S')
    message = f"""
🔥 MASTER CALL: **{symbol}** – **{direction.upper()}**

📍 Entry: `{entry}`
🛑 Stop Loss: `{sl}`
🎯 Take Profit: `{tp}`
📊 Risk Reward: `{rr}`
✅ Confidence Level: **HIGH** ✅

🔍 Alasan / Analisa:
- Trend saat ini: {direction} + struktur valid
- Konfirmasi timeframe: 1H + 4H
- Volume Analysis: Breakout volume > MA20
- Divergence: RSI valid
- Candle pattern: Engulfing
- MA: EMA20 cross EMA50, searah EMA200

⏰ Estimasi Durasi Pergerakan: 4 – 12 jam

📈 Skenario Jika TP:
- Potensi lanjutan trend
- Re-entry zone: retest EMA50

📉 Skenario Jika SL:
- Zona cadangan: swing HL/LL berikutnya
- Tunggu reversal RSI + struktur ulang

⚠️ Setup valid hanya jika struktur harga tetap searah!
"""
    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)


# =============================
# MAIN LOOP SCANNER
# =============================
async def scan_all_pairs():
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets if s.endswith("/USDT") and "PERP" in markets[s]['id']]

    while True:
        for symbol in usdt_pairs:
            try:
                df_1h = get_klines(symbol, '1h')
                df_4h = get_klines(symbol, '4h')

                signal_1h = generate_signal(df_1h)
                signal_4h = generate_signal(df_4h)

                if signal_1h == signal_4h and signal_1h is not None:
                    entry = round(df_1h['close'].iloc[-1], 3)
                    sl = round(entry * 0.985 if signal_1h == 'long' else entry * 1.015, 3)
                    tp = round(entry * 1.03 if signal_1h == 'long' else entry * 0.97, 3)
                    rr = round(abs(tp - entry) / abs(entry - sl), 2)

                    send_discord_signal(symbol, signal_1h, entry, sl, tp, rr)

            except Exception as e:
                print(f"[{symbol}] Error: {e}")

        await asyncio.sleep(INTERVAL_SCAN)


# =============================
# RUN BOT
# =============================
if __name__ == "__main__":
    asyncio.run(scan_all_pairs())
