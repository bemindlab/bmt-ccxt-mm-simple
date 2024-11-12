import pandas as pd
from datetime import datetime, timedelta
from src.utils.config import initialize_exchange, load_config_with_bot_name


class PnLCalculator:
    def __init__(self):
        """
        Initialize the PnLCalculator.
        """
        self.bot_name = None
        self.config = None
        self.exchange_id = None
        self.trading_pair = None
        self.exchange = None

    def initialize_bot(self, bot_name, config_path):
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

            # find the market
            self.market = self.markets[self.trading_pair]

        except Exception as e:
            print(f"Error initializing bot: {e}")
            return None
