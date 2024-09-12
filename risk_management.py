import numpy as np

class RiskManagement:
    def __init__(self, config):
        self.initial_risk_per_trade = config['risk_per_trade']
        self.max_risk_per_trade = config['max_risk_per_trade']
        self.max_leverage = config['max_leverage']
        self.stop_loss_pct = config['stop_loss_pct']
        self.risk_free_rate = 0.02  # Assume 2% risk-free rate

    def calculate_stop_loss_take_profit(self, entry_price, action):
        stop_loss_pct = self.stop_loss_pct
        take_profit_pct = stop_loss_pct * 1.5  # Risk-reward ratio of 1:1.5

        if action == "BUY":
            stop_loss = entry_price * (1 - stop_loss_pct)
            take_profit = entry_price * (1 + take_profit_pct)
        else:  # SELL
            stop_loss = entry_price * (1 + stop_loss_pct)
            take_profit = entry_price * (1 - take_profit_pct)

        return stop_loss, take_profit

    def calculate_leverage(self, volatility):
        # Calculate leverage based on volatility
        max_leverage = min(self.max_leverage, 1 / volatility)
        return round(max_leverage, 1)

    def calculate_position_size(self, account_balance, entry_price, stop_loss):
        risk_amount = account_balance * self.initial_risk_per_trade
        position_size = risk_amount / abs(entry_price - stop_loss)
        return position_size

    def calculate_kelly_criterion(self, win_rate, avg_win, avg_loss):
        q = 1 - win_rate
        return (win_rate / q) - (avg_loss / avg_win)

    def calculate_var(self, returns, confidence_level=0.95):
        return np.percentile(returns, (1 - confidence_level) * 100)

    def calculate_sharpe_ratio(self, returns):
        excess_returns = returns - self.risk_free_rate
        return np.mean(excess_returns) / np.std(excess_returns) * np.sqrt(252)  # Annualized