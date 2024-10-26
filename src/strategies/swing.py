import os
import time
import logging
import pandas as pd
import numpy as np
import ccxt
from dotenv import load_dotenv
from ta.trend import MACD

# Load environment variables
load_dotenv()


class SwingTradingStrategy:
    def __init__(self, trading_pair="BTC/USDT", position_size=0.001, test_mode=False):
        # Initialize Binance Futures API with your credentials
        self.api_key = os.environ.get("BINANCE_API_KEY")
        self.api_secret = os.environ.get("BINANCE_API_SECRET")
        self.exchange = ccxt.binance(
            {
                "apiKey": self.api_key,
                "secret": self.api_secret,
                "options": {"defaultType": "future"},  # Enable Binance Futures
                "enableRateLimit": True,
            }
        )

        self.trading_pair = trading_pair.upper()
        self.position_size = float(position_size)
        self.test_mode = test_mode

        # Configure logging
        logging.basicConfig(
            level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s"
        )
        logging.info(
            f"Initialized TradingBot for {self.trading_pair} with position size {self.position_size}"
        )

    def fetch_candles(self, since=None):
        """Fetch 15-minute candlestick (OHLCV) data for the trading pair."""
        try:
            candles = self.exchange.fetch_ohlcv(
                self.trading_pair, timeframe="15m", limit=200, since=since
            )
            df = pd.DataFrame(
                candles, columns=["timestamp", "open", "high", "low", "close", "volume"]
            )
            df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")
            return df
        except Exception as e:
            logging.error(f"Error fetching candles: {e}")
            return pd.DataFrame()  # Return empty DataFrame on error

    def resample_45m(self, df):
        """Resample to 45 minutes by combining three 15-minute periods."""
        df.set_index("timestamp", inplace=True)
        df_45m = (
            df.resample("45T")
            .agg(
                {
                    "open": "first",
                    "high": "max",
                    "low": "min",
                    "close": "last",
                    "volume": "sum",
                }
            )
            .dropna()
        )
        return df_45m

    def compute_indicators(self, df):
        """Compute technical indicators."""
        df["SMA_45m"] = MACD.SMA(df["close"], timeperiod=45)
        df["RSI"] = MACD.RSI(df["close"], timeperiod=14)
        df["upper_band"], df["middle_band"], df["lower_band"] = talib.BBANDS(
            df["close"], timeperiod=20
        )
        return df

    def get_current_position(self):
        """Check if there is an existing open position."""
        try:
            positions = self.exchange.fapiPrivateGetPositionRisk()
            for position in positions:
                if position["symbol"] == self.trading_pair.replace("/", ""):
                    position_amt = float(position["positionAmt"])
                    return position_amt
            return 0.0
        except Exception as e:
            logging.error(f"Error fetching current position: {e}")
            return 0.0

    def place_order(self, side, amount, price=None):
        """Place a limit or market order on Binance Futures."""
        try:
            order_type = "limit" if price else "market"
            params = {"timeInForce": "GTC"} if price else {}
            order = self.exchange.create_order(
                symbol=self.trading_pair,
                type=order_type,
                side=side,
                amount=amount,
                price=price,
                params=params,
            )
            logging.info(f"Order placed: {order}")
        except Exception as e:
            logging.error(f"Error placing order: {e}")

    def execute_strategy(self, df):
        """Execute the trading strategy based on technical indicators."""
        if df.empty or "SMA_45m" not in df.columns or np.isnan(df["SMA_45m"].iloc[-1]):
            logging.warning("Insufficient data to compute indicators.")
            return

        current_price = df["close"].iloc[-1]
        sma_45m = df["SMA_45m"].iloc[-1]
        logging.info(f"Current Price: {current_price}, SMA_45m: {sma_45m}")

        # Check for existing positions
        position_amt = self.get_current_position()
        logging.info(f"Current Position Amount: {position_amt}")

        # Buy if the current price is 5% below the 45-minute SMA and no existing long position
        if current_price < sma_45m * 0.95 and position_amt >= 0:
            logging.info("Signal to Buy.")
            if self.test_mode:
                logging.info("Test Mode: Buy order simulated.")
            else:
                self.place_order("buy", self.position_size)

        # Sell if the current price is 5% above the 45-minute SMA and no existing short position
        elif current_price > sma_45m * 1.05 and position_amt <= 0:
            logging.info("Signal to Sell.")
            if self.test_mode:
                logging.info("Test Mode: Sell order simulated.")
            else:
                self.place_order("sell", self.position_size)

        else:
            logging.info("No trading signal detected.")

    def backtest(self, days=7):
        """Perform a backtest using historical data."""
        since = self.exchange.parse8601(
            (pd.Timestamp.utcnow() - pd.Timedelta(days=days)).strftime(
                "%Y-%m-%dT%H:%M:%SZ"
            )
        )
        df = self.fetch_candles(since=since)
        df_45m = self.resample_45m(df)
        df_45m = self.compute_indicators(df_45m)

        # Iterate over the DataFrame rows and simulate trading
        position = 0  # 0: No position, 1: Long, -1: Short
        for index in range(len(df_45m)):
            current_data = df_45m.iloc[: index + 1]
            if current_data.empty or np.isnan(current_data["SMA_45m"].iloc[-1]):
                continue  # Skip if indicators cannot be computed

            current_price = current_data["close"].iloc[-1]
            sma_45m = current_data["SMA_45m"].iloc[-1]

            if current_price < sma_45m * 0.95 and position == 0:
                logging.info(
                    f"[{current_data.index[-1]}] Backtest Buy at {current_price}"
                )
                position = 1  # Enter long position

            elif current_price > sma_45m * 1.05 and position == 0:
                logging.info(
                    f"[{current_data.index[-1]}] Backtest Sell at {current_price}"
                )
                position = -1  # Enter short position

            # Exit conditions can be added here

        logging.info("Backtest completed.")

    def run(self):
        """Main loop to run the trading bot."""
        while True:
            try:
                df = self.fetch_candles()
                df_45m = self.resample_45m(df)
                df_45m = self.compute_indicators(df_45m)
                self.execute_strategy(df_45m)

                # Sleep until the next 15-minute interval
                current_minute = pd.Timestamp.utcnow().minute
                sleep_minutes = (15 - (current_minute % 15)) % 15
                sleep_seconds = sleep_minutes * 60 - pd.Timestamp.utcnow().second
                logging.info(f"Sleeping for {sleep_minutes} minutes.")
                time.sleep(sleep_seconds if sleep_seconds > 0 else 60)
            except Exception as e:
                logging.error(f"Error in main loop: {e}")
                time.sleep(60)  # Sleep for 1 minute before retrying


if __name__ == "__main__":
    # Get trading pair from user input
    trading_pair_input = input("Enter the trading pair (e.g., BTC/USDT): ").strip()
    trading_pair = trading_pair_input.upper() if trading_pair_input else "BTC/USDT"
    print(f"Using trading pair: {trading_pair}")

    # Get position size from user input
    position_size_input = input("Enter the position size (e.g., 0.001): ").strip()
    position_size = float(position_size_input) if position_size_input else 0.001
    print(f"Using position size: {position_size}")

    # Get test or live mode from user input
    test_or_live = (
        input("Enter 'test' for backtest or 'live' for live trading: ").strip().lower()
    )
    test_mode = True if test_or_live == "test" else False

    bot = SwingTradingStrategy(
        trading_pair=trading_pair, position_size=position_size, test_mode=test_mode
    )

    if test_mode:
        bot.backtest(days=7)
    else:
        bot.run()
