import numpy as np
import pandas as pd
from sklearn.preprocessing import MinMaxScaler
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import LSTM, Dense, Dropout
from tensorflow.keras.optimizers import Adam

class EnhancedMLPredictor:
    def __init__(self, lookback=60, features=['open', 'high', 'low', 'close', 'volume']):
        self.lookback = lookback
        self.features = features
        self.model = self._build_lstm_model()
        self.scaler = MinMaxScaler()

    def _build_lstm_model(self):
        model = Sequential([
            LSTM(100, return_sequences=True, input_shape=(self.lookback, len(self.features))),
            Dropout(0.2),
            LSTM(100, return_sequences=False),
            Dropout(0.2),
            Dense(1)
        ])
        model.compile(optimizer=Adam(learning_rate=0.001), loss='mse')
        return model

    def prepare_data(self, df):
        df_featured = self._engineer_features(df)
        X = df_featured[self.features].values
        y = df_featured['close'].shift(-1).values[:-1]
        X = X[:-1]

        X_scaled = self.scaler.fit_transform(X)
        X_seq = np.array([X_scaled[i-self.lookback:i] for i in range(self.lookback, len(X_scaled))])
        y_seq = y[self.lookback-1:]

        return X_seq, y_seq

    def _engineer_features(self, df):
        df = df.copy()
        df['MA_10'] = df['close'].rolling(window=10).mean()
        df['RSI'] = self._calculate_rsi(df['close'])
        df['MACD'] = self._calculate_macd(df['close'])
        return df

    def _calculate_rsi(self, prices, period=14):
        delta = prices.diff()
        gain