import pandas as pd
import numpy as np


class SignalGenerator:
    def __init__(self, config, risk_management, ml_predictor, market_regime_detector):
        self.config = config
        self.risk_management = risk_management
        self.ml_predictor = ml_predictor
        self.market_regime_detector = market_regime_detector

    def generate_signal(self, df, symbol):
        # Detect market regime
        regime, regime_probs = self.market_regime_detector.detect_regime(df['close'])

        # Generate prediction using ML model
        ml_prediction = self.ml_predictor.predict(df)

        # Calculate technical indicators
        df = self._calculate_indicators(df)

        # Generate signal based on strategies
        momentum_signal = self._momentum_strategy(df)
        mean_reversion_signal = self._mean_reversion_strategy(df)
        breakout_signal = self._breakout_strategy(df)

        # Combine signals
        combined_signal = self._combine_signals(momentum_signal, mean_reversion_signal, breakout_signal, ml_prediction)

        if combined_signal != 0:
            action = "BUY" if combined_signal > 0 else "SELL"
            entry_price = df['close'].iloc[-1]
            stop_loss, take_profit = self.risk_management.calculate_stop_loss_take_profit(entry_price, action)
            leverage = self.risk_management.calculate_leverage(df['close'].pct_change().std())

            explanation = self._generate_explanation(df, regime, combined_signal, ml_prediction)

            return {
                "symbol": symbol,
                "action": action,
                "entry_price": entry_price,
                "stop_loss": stop_loss,
                "take_profit": take_profit,
                "leverage": leverage,
                "explanation": explanation
            }

        return None

    def _calculate_indicators(self, df):
        df['SMA_50'] = df['close'].rolling(window=50).mean()
        df['SMA_200'] = df['close'].rolling(window=200).mean()
        df['RSI'] = self._calculate_rsi(df['close'])
        return df

    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=period).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=period).mean()
        rs = gain / loss
        return 100 - (100 / (1 + rs))

    def _momentum_strategy(self, df):
        if df['close'].iloc[-1] > df['SMA_50'].iloc[-1] and df['RSI'].iloc[-1] < 70:
            return 1
        elif df['close'].iloc[-1] < df['SMA_50'].iloc[-1] and df['RSI'].iloc[-1] > 30:
            return -1
        return 0

    def _mean_reversion_strategy(self, df):
        if df['RSI'].iloc[-1] < 30 and df['close'].iloc[-1] < df['SMA_200'].iloc[-1]:
            return 1
        elif df['RSI'].iloc[-1] > 70 and df['close'].iloc[-1] > df['SMA_200'].iloc[-1]:
            return -1
        return 0

    def _breakout_strategy(self, df):
        highest_high = df['high'].rolling(window=20).max()
        lowest_low = df['low'].rolling(window=20).min()

        if df['close'].iloc[-1] > highest_high.iloc[-2]:
            return 1
        elif df['close'].iloc[-1] < lowest_low.iloc[-2]:
            return -1
        return 0

    def _combine_signals(self, momentum, mean_reversion, breakout, ml_prediction):
        combined = (
                self.config['capital_allocation']['momentum'] * momentum +
                self.config['capital_allocation']['mean_reversion'] * mean_reversion +
                self.config['capital_allocation']['breakout'] * breakout
        )

        # Incorporate ML prediction
        if (combined > 0 and ml_prediction > 0) or (combined < 0 and ml_prediction < 0):
            return combined * 1.2  # Strengthen the signal if ML agrees
        elif (combined > 0 and ml_prediction < 0) or (combined < 0 and ml_prediction > 0):
            return combined * 0.8  # Weaken the signal if ML disagrees
        return combined

    def _generate_explanation(self, df, regime, signal, ml_prediction):
        explanation = f"In the past {len(df)} periods, "

        if signal > 0:
            explanation += "there has been a bullish trend. "
        elif signal < 0:
            explanation += "there has been a bearish trend. "

        explanation += f"The current market regime is {self.market_regime_detector.regime_description(regime)}. "

        if ml_prediction > 0:
            explanation += "The machine learning model predicts an upward movement. "
        elif ml_prediction < 0:
            explanation += "The machine learning model predicts a downward movement. "

        explanation += f"The RSI is currently at {df['RSI'].iloc[-1]:.2f}, "

        if df['close'].iloc[-1] > df['SMA_50'].iloc[-1]:
            explanation += "and the price is above the 50-period moving average. "
        else:
            explanation += "and the price is below the 50-period moving average. "

        return explanation