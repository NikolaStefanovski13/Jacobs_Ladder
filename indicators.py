import pandas as pd
import numpy as np

class Indicators:
    @staticmethod
    def calculate_atr(df, period=14):
        high_low = df['high'] - df['low']
        high_close = (df['high'] - df['close'].shift()).abs()
        low_close = (df['low'] - df['close'].shift()).abs()
        tr = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
        atr = tr.rolling(window=period).mean()
        return atr

    @staticmethod
    def chandelier_exit(df, atr, atr_period, multiplier=3.0):
        highest_high = df['high'].rolling(window=atr_period).max()
        return highest_high - (atr * multiplier)

    @staticmethod
    def moving_average(df, window=50):
        return df['close'].rolling(window=window).mean()

    @staticmethod
    def fibonacci_retracement(df):
        high = df['close'].max()
        low = df['close'].min()
        diff = high - low
        return {
            "0%": high,
            "23.6%": high - 0.236 * diff,
            "38.2%": high - 0.382 * diff,
            "50%": high - 0.5 * diff,
            "61.8%": high - 0.618 * diff,
            "78.6%": high - 0.786 * diff,
            "100%": low
        }

    @staticmethod
    def calculate_rsi(prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def calculate_macd(prices, fast=12, slow=26, signal=9):
        fast_ema = prices.ewm(span=fast, adjust=False).mean()
        slow_ema = prices.ewm(span=slow, adjust=False).mean()
        macd = fast_ema - slow_ema
        signal_line = macd.ewm(span=signal, adjust=False).mean()
        histogram = macd - signal_line
        return pd.DataFrame({
            'MACD': macd,
            'Signal': signal_line,
            'Histogram': histogram
        })

    @staticmethod
    def bollinger_bands(df, window=20, num_std=2):
        rolling_mean = df['close'].rolling(window=window).mean()
        rolling_std = df['close'].rolling(window=window).std()
        upper_band = rolling_mean + (rolling_std * num_std)
        lower_band = rolling_mean - (rolling_std * num_std)
        return pd.DataFrame({
            'Upper': upper_band,
            'Middle': rolling_mean,
            'Lower': lower_band
        })