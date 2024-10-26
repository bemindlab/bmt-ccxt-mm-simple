import logging
import random
from time import sleep
from datetime import datetime
from src.utils.config import initialize_exchange, load_config_with_bot_name


class MarketPriceStrategy:
    def __init__(self):
        """Initialize the MarketPriceStrategy class."""
        self.bot_name = None
        self.config = None
        self.exchange_id = None
        self.trading_pair = None
        self.exchange = None
        self.market = None
        self.order_amount = 0

    def initialize_bot(self, bot_name, config_path, order_amount=1, target_volume=1):
        """Initialize the bot with the exchange and trading pair."""
        try:
            self.bot_name = bot_name
            self.config = load_config_with_bot_name(bot_name, config_path)
            self.exchange = initialize_exchange(self.config)
            self.trading_pair = self.config["bot"]["trading_pair"]
            self.exchange_id = self.config["bot"]["exchange"]

            print(f"Initialized bot: {self.bot_name}")
            print(f"Exchange: {self.exchange_id}")
            print(f"Trading pair: {self.trading_pair}")

            # Get the market and quote currency
            self.markets = self.exchange.load_markets()

            # find the market
            self.market = self.markets[self.trading_pair]
            self.order_amount = order_amount
            self.target_volume = target_volume

        except Exception as e:
            print(f"Error initializing bot: {e}")
            return None

    def calculate_order_amount(self, current_price, side):
        """Calculate the order amount based on the current balance."""
        try:
            if self.exchange.id == "mexc":
                return float(self.order_amount / current_price)

            elif self.exchange.id == "bitget" or self.exchange.id == "gate":
                if side == "sell":
                    return float(self.order_amount / current_price)

            elif self.exchange.id == "bybit":
                return float(self.order_amount / current_price)

            return self.order_amount

        except Exception as e:
            logging.error(f"Error calculating order amount: {e}")

    def place_market_order(self, side):
        """Place a market order (buy or sell) at the current market price."""
        try:
            # Fetch the current market price
            ticker = self.exchange.fetch_ticker(self.trading_pair)
            current_price = ticker["last"]
            current_volume = ticker["quoteVolume"]

            if current_price <= 0:
                raise Exception("current price is 0")

            trade_amount = self.calculate_order_amount(current_price, side)
            print("=" * 50)
            print(f"= Bot Name: {self.bot_name} : {side}")
            print("=" * 50)
            print(f"- Trading Pair: {self.trading_pair}")
            print(f"- Order Amount: {self.order_amount}")
            print(f"- Trade Amount {trade_amount}")
            print(f"- Current price: {current_price}")
            print(f"- Current Volume: {current_volume}")
            print(f"- Target Volume: {self.target_volume}")

            if current_volume > self.target_volume:
                print("-" * 50)
                print("Target volume reached")
                print("-" * 50, "\n")
                raise Exception("Target volume reached")

            # Place the market order

            self.exchange.create_order(
                self.trading_pair, "market", side, trade_amount, current_price
            )

            print("-" * 50)
            print("\n")

        except Exception as e:
            # if max orders limit reached, cancel all open orders and place the order again
            if "Order would trigger immediately" in str(e):
                self.cancel_orders()
            else:
                logging.error(f"Error placing market order: {e}")

    def execute(self):
        """Main logic to run the market-making strategy."""
        try:
            self.order_amount = self.order_amount
            self.place_market_order("buy")

            # Sleep for a random time between 1 to 2 seconds
            sleep(random.uniform(1, 3))
            print("-" * 20, "==========", "-" * 20, "\n")

            self.order_amount = self.order_amount
            self.place_market_order("sell")

            # next iteration
            print("next order ...")

        except Exception as e:
            logging.error(f"Error executing market-making strategy: {e}")
