# discord_alert.py
import requests

def send_discord_signal(symbol, direction, sl, tp, entry, rr, timeframe="1H + 4H"):

    message = f"""
🔥 MASTER CALL: **{symbol}** – **{direction.upper()}**

📍 Entry: `{entry}`
🛑 Stop Loss: `{sl}`
🎯 Take Profit: `{tp}`
📊 Risk Reward: `{rr}`
✅ Confidence Level: **HIGH** ✅

🔍 Alasan / Analisa:
- Trend saat ini: {direction} + struktur valid
- Konfirmasi timeframe: {timeframe}
- Volume Analysis: Breakout volume > MA20
- Divergence: RSI valid
- Candle pattern: Engulfing
- MA: EMA20 cross EMA50, di atas/bawah EMA200

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
    requests.post("https://discord.com/api/webhooks/1360089106150854777/CUJWPc7hn_2G6qd8bJp3r13QKyMkUSVD7zSl_JqSJ8-Ns_BofNNu0Cr1S7cjEw5Ob_gQ", json=payload)
