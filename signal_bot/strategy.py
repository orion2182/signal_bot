import ta
import numpy as np

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
    candle_range = df['high'].iloc[-1] - df['low'].iloc[-1]
    body_size = abs(df['close'].iloc[-1] - df['open'].iloc[-1])
    candle_valid = body_size > (0.6 * candle_range)
    return spike and candle_valid

def detect_divergence(df):
    df['rsi'] = ta.momentum.rsi(df['close'], window=14)
    recent_lows = df['close'].iloc[-5:].values
    recent_rsi = df['rsi'].iloc[-5:].values

    if recent_lows[-2] < recent_lows[-1] and recent_rsi[-2] > recent_rsi[-1]:  # hidden bullish
        return 'hidden_bullish'
    elif recent_lows[-2] > recent_lows[-1] and recent_rsi[-2] < recent_rsi[-1]:  # regular bullish
        return 'regular_bullish'
    return None

def detect_candle_pattern(df):
    last_open = df['open'].iloc[-1]
    last_close = df['close'].iloc[-1]
    last_high = df['high'].iloc[-1]
    last_low = df['low'].iloc[-1]

    body = abs(last_close - last_open)
    upper_shadow = last_high - max(last_close, last_open)
    lower_shadow = min(last_close, last_open) - last_low

    if body < upper_shadow and body < lower_shadow:
        return 'doji'
    elif last_close > last_open and body > (upper_shadow + lower_shadow):
        return 'bullish_engulfing'
    elif last_close < last_open and body > (upper_shadow + lower_shadow):
        return 'bearish_engulfing'
    return None

def generate_signal(df):
    direction = ema_cross(df)
    vol = volume_spike(df)
    div = detect_divergence(df)
    pattern = detect_candle_pattern(df)

    if direction == 'long' and vol and div in ['regular_bullish', 'hidden_bullish'] and pattern in ['bullish_engulfing']:
        return 'long'
    elif direction == 'short' and vol and pattern == 'bearish_engulfing':
        return 'short'
    return None
