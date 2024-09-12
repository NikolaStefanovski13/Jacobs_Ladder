import logging
import yaml
import yfinance as yf
from datetime import datetime, timedelta

def setup_logging(log_level: str) -> None:
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        filename='signals_bot.log',
        filemode='a'
    )
    console = logging.StreamHandler()
    console.setLevel(log_level)
    logging.getLogger('').addHandler(console)

def load_config(file_path):
    with open(file_path, 'r') as file:
        return yaml.safe_load(file)

def fetch_ohlcv(symbol, timeframe, history_length):
    try:
        end_date = datetime.now()
        start_date = end_date - timedelta(days=7)  # Fetch 7 days of data
        df = yf.Ticker(symbol).history(interval=timeframe, start=start_date, end=end_date)
        return df
    except Exception as e:
        logging.error(f"An error occurred while fetching data for {symbol}: {str(e)}")
        return None

def format_signal(signal):
    return f"""
    Symbol: {signal['symbol']}
    Action: {signal['action']}
    Entry Price: {signal['entry_price']:.2f}
    Stop Loss: {signal['stop_loss']:.2f}
    Take Profit: {signal['take_profit']:.2f}
    Leverage: {signal['leverage']}x
    Generated At: {signal['generated_at']}
    Valid Until: {signal['valid_until']}
    Explanation: {signal['explanation']}
    """

def fetch_all_ohlcv(symbols, timeframe, history_length):
    return {symbol: fetch_ohlcv(symbol, timeframe, history_length) for symbol in symbols}
