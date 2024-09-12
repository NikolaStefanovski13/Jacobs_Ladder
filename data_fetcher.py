# data_fetcher.py

import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta


class YFinanceDataFetcher:
    def __init__(self, config):
        self.timeframe = config['data_parameters']['timeframe']
        self.history_length = config['data_parameters']['history_length']

    def fetch_historical_data(self, symbol):
        try:
            end_date = datetime.now()
            start_date = end_date - pd.Timedelta(self.history_length)

            ticker = yf.Ticker(symbol)
            df = ticker.history(start=start_date, end=end_date, interval=self.timeframe)

            df.index = df.index.tz_localize(None)  # Remove timezone info
            return df
        except Exception as e:
            print(f"Error fetching data for {symbol}: {e}")
            return pd.DataFrame()

    def get_current_price(self, symbol):
        try:
            ticker = yf.Ticker(symbol)
            return ticker.info['regularMarketPrice']
        except Exception as e:
            print(f"Error fetching current price for {symbol}: {e}")
            return None