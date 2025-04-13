import ccxt
import asyncio
from config import INTERVAL_SCAN
from strategy import generate_signal
from utils import get_klines, send_discord_signal

exchange = ccxt.binance({
    'enableRateLimit': True,
    'options': {'defaultType': 'future'}
})

async def scan_pairs():
    markets = exchange.load_markets()
    usdt_pairs = [s for s in markets if s.endswith("/USDT") and "PERP" in markets[s]['id']]

    while True:
        for symbol in usdt_pairs:
            try:
                df_1h = get_klines(exchange, symbol, '1h')
                df_4h = get_klines(exchange, symbol, '4h')

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
