import numpy as np
import pandas as pd

class PerformanceAnalytics:
    def __init__(self):
        self.signals = []

    def add_signal(self, signal):
        self.signals.append(signal)

    def calculate_metrics(self):
        if not self.signals:
            return {}

        df = pd.DataFrame(self.signals)
        df['return'] = df.groupby('symbol').apply(self._calculate_returns).reset_index(level=0, drop=True)

        total_signals = len(df)
        correct_signals = len(df[df['return'] > 0])
        accuracy = correct_signals / total_signals if total_signals > 0 else 0

        avg_return = df['return'].mean()
        sharpe_ratio = self._calculate_sharpe_ratio(df['return'])

        return {
            'total_signals': total_signals,
            'accuracy': accuracy,
            'avg_return': avg_return,
            'sharpe_ratio': sharpe_ratio
        }

    def _calculate_returns(self, group):
        entry_price = group['entry_price'].iloc[0]
        exit_price = group['entry_price'].iloc[-1]  # Use the last signal's entry price as exit price
        return (exit_price - entry_price) / entry_price if group['action'].iloc[0] == 'BUY' else (entry_price - exit_price) / entry_price

    def _calculate_sharpe_ratio(self, returns, risk_free_rate=0.02):
        excess_returns = returns - risk_free_rate
        return np.sqrt(252) * excess_returns.mean() / excess_returns.std() if excess_returns.std() != 0 else 0

    def get_best_performing_symbols(self, top_n=5):
        if not self.signals:
            return []

        df = pd.DataFrame(self.signals)
        df['return'] = df.groupby('symbol').apply(self._calculate_returns).reset_index(level=0, drop=True)
        return df.groupby('symbol')['return'].mean().nlargest(top_n).index.tolist()

    def get_worst_performing_symbols(self, bottom_n=5):
        if not self.signals:
            return []

        df = pd.DataFrame(self.signals)
        df['return'] = df.groupby('symbol').apply(self._calculate_returns).reset_index(level=0, drop=True)
        return df.groupby('symbol')['return'].mean().nsmallest(bottom_n).index.tolist()