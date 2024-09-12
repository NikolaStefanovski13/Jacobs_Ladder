# main.py

import asyncio
import logging
from data_fetcher import YFinanceDataFetcher
from strategy import Strategy
from risk_management import DynamicRiskManagement
from ml_predictor import EnhancedMLPredictor
from market_regime_detector import MarketRegimeDetector
from utils import setup_logging, load_config
import pandas as pd
import time


async def generate_signal(symbol, df, current_price, strategies, risk_management, ml_predictor, market_regime_detector):
    if df.empty:
        return None

    regime, regime_probs = market_regime_detector.detect_regime(df['Close'])
    ml_prediction = ml_predictor.predict(df)

    signals = {}
    for strategy_name, strategy in strategies.items():
        signal = strategy.generate_signal(df, ml_prediction, regime)
        if signal['action'] in ['buy', 'sell']:
            entry_price = current_price
            stop_loss_price = signal['stop_loss']
            position_size = risk_management.calculate_position_size(entry_price, stop_loss_price,
                                                                    df['Close'].pct_change().std())
            leverage = min(risk_management.calculate_leverage(signal['action'], entry_price, stop_loss_price),
                           config['risk_management']['max_leverage'])

            explanation = f"""
            Signal for {symbol} ({strategy_name} strategy):
            Action: {signal['action'].upper()}
            Entry Price: {entry_price:.2f}
            Stop Loss: {stop_loss_price:.2f}
            Take Profit: {signal['take_profit']:.2f}
            Leverage: {leverage:.2f}x
            Position Size: {position_size:.4f}

            Explanation:
            {strategy.explain_signal(df, signal, regime)}

            Market Regime: {market_regime_detector.regime_description(regime)}
            ML Prediction: {ml_prediction:.2f}
            """

            signals[strategy_name] = {
                'action': signal['action'],
                'entry_price': entry_price,
                'stop_loss': stop_loss_price,
                'take_profit': signal['take_profit'],
                'leverage': leverage,
                'position_size': position_size,
                'explanation': explanation,
                'timestamp': pd.Timestamp.now()
            }

    return signals


async def run_bot(config):
    data_fetcher = YFinanceDataFetcher(config)

    strategies = {
        'momentum': Strategy(config['strategy'], 'momentum'),
        'mean_reversion': Strategy(config['strategy'], 'mean_reversion'),
        'breakout': Strategy(config['strategy'], 'breakout')
    }

    risk_management = DynamicRiskManagement(config['risk_management'])
    ml_predictor = EnhancedMLPredictor()
    market_regime_detector = MarketRegimeDetector()

    last_signal_time = {}
    all_signals = []

    while True:
        for symbol in config['trading']['symbols']:
            try:
                current_time = pd.Timestamp.now()

                # Check cooldown period
                if symbol in last_signal_time and (current_time - last_signal_time[symbol]).total_seconds() < \
                        config['trading']['cooldown_period']:
                    continue

                df = data_fetcher.fetch_historical_data(symbol)
                current_price = data_fetcher.get_current_price(symbol)

                if df.empty or current_price is None:
                    logging.warning(f"No data available for {symbol}, skipping...")
                    continue

                signals = await generate_signal(symbol, df, current_price, strategies, risk_management, ml_predictor,
                                                market_regime_detector)

                if signals:
                    for strategy_name, signal in signals.items():
                        logging.info(f"\n{signal['explanation']}")
                        all_signals.append({**signal, 'symbol': symbol, 'strategy': strategy_name})
                    last_signal_time[symbol] = current_time
                else:
                    logging.info(f"No signals generated for {symbol}")

            except Exception as e:
                logging.error(f"Error processing {symbol}: {e}")

        # Save signals to CSV
        signals_df = pd.DataFrame(all_signals)
        signals_df.to_csv(config['output']['signal_file'], index=False)

        # Remove expired signals
        current_time = pd.Timestamp.now()
        all_signals = [signal for signal in all_signals if
                       (current_time - signal['timestamp']).total_seconds() < config['trading'][
                           'signal_validity_window']]

        await asyncio.sleep(config['trading']['iteration_interval'])


async def main():
    global config
    config = load_config('config.yaml')
    setup_logging(config['logging']['level'], config['logging']['file'])

    try:
        await run_bot(config)
    except KeyboardInterrupt:
        logging.info("Bot stopped by user.")
    except Exception as e:
        logging.error(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    asyncio.run(main())