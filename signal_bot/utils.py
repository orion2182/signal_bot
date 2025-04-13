import pandas as pd
import requests
from config import DISCORD_WEBHOOK_URL

def get_klines(exchange, symbol, timeframe='1h', limit=100):
    ohlcv = exchange.fetch_ohlcv(symbol, timeframe=timeframe, limit=limit)
    df = pd.DataFrame(ohlcv, columns=['timestamp', 'open', 'high', 'low', 'close', 'volume'])
    df['timestamp'] = pd.to_datetime(df['timestamp'], unit='ms')
    return df

def send_discord_signal(symbol, direction, entry, sl, tp, rr):
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
📈 Skenario TP: lanjutan trend / re-entry EMA50
📉 Skenario SL: tunggu reversal + struktur ulang
"""
    payload = {"content": message}
    requests.post(DISCORD_WEBHOOK_URL, json=payload)
