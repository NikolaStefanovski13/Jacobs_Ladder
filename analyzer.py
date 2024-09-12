from indicators import Indicators
import logging

class DataAnalyzer:
    def __init__(self, data):
        self.data = data
        self.indicators = Indicators()

    def analyze_fibonacci_retracement(self):
        levels = self.indicators.fibonacci_retracement(self.data)
        current_price = self.data['close'].iloc[-1]

        analysis = {}
        for level, price in levels.items():
            analysis[level] = price

        if current_price >= levels["23.6%"]:
            analysis['outlook'] = "Bullish"
        elif current_price >= levels["38.2%"]:
            analysis['outlook'] = "Neutral"
        elif current_price >= levels["61.8%"]:
            analysis['outlook'] = "Bearish"
        else:
            analysis['outlook'] = "Strongly Bearish"

        return analysis

    def analyze_moving_averages(self):
        ma_50 = self.indicators.moving_average(self.data, window=50)
        ma_200 = self.indicators.moving_average(self.data, window=200)

        current_price = self.data['close'].iloc[-1]
        analysis = {
            'MA50': ma_50.iloc[-1],
            'MA200': ma_200.iloc[-1],
        }

        if current_price > ma_50.iloc[-1] > ma_200.iloc[-1]:
            analysis['outlook'] = "Bullish"
        elif current_price < ma_50.iloc[-1] < ma_200.iloc[-1]:
            analysis['outlook'] = "Bearish"
        else:
            analysis['outlook'] = "Neutral"

        return analysis

    def analyze_rsi(self):
        rsi = self.indicators.calculate_rsi(self.data['close'])
        current_rsi = rsi.iloc[-1]

        analysis = {
            'RSI': current_rsi,
        }

        if current_rsi > 70:
            analysis['outlook'] = "Overbought"
        elif current_rsi < 30:
            analysis['outlook'] = "Oversold"
        else:
            analysis['outlook'] = "Neutral"

        return analysis