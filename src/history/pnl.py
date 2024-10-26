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
        self.market = None
        self.quote_currency = None
        self.base_currency = None

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

            # Get the market and quote currency
            self.markets = self.exchange.load_markets()

            # find the market
            self.market = self.markets[self.trading_pair]

            # Get the quote and base currency
            self.quote_currency = self.market["quote"]
            self.base_currency = self.market["base"]

            print(f"Quote currency: {self.quote_currency}")
            print(f"Base currency: {self.base_currency}")

        except Exception as e:
            print(f"Error initializing bot: {e}")
            return None

    def fetch_trades(self, since, until=None):
        """Fetch trades for the trading pair within the specified date range."""
        if self.exchange is None:
            print("Exchange not initialized.")
            return []
        if not self.exchange.has["fetchMyTrades"]:
            print(
                f"The exchange '{self.exchange_id}' does not support 'fetch_my_trades' method."
            )
            return []
        all_trades = []
        limit = 1000  # Maximum number of trades per request for Binance
        end_time = until if until else self.exchange.milliseconds()
        max_time_range = 7 * 24 * 60 * 60 * 1000  # 7 days in milliseconds

        print(
            f"Fetching trades from {datetime.utcfromtimestamp(since / 1000)} to {datetime.utcfromtimestamp(end_time / 1000)}"
        )

        while since < end_time:
            current_end_time = min(since + max_time_range - 1, end_time)
            params = {"startTime": since, "endTime": current_end_time, "limit": limit}
            try:
                trades = self.exchange.fetch_my_trades(
                    symbol=self.trading_pair,
                    since=None,  # 'since' is being handled via 'params'
                    limit=limit,
                    params=params,
                )
                if not trades:
                    since += max_time_range  # Move to the next time window
                    continue
                all_trades.extend(trades)
                last_trade_time = trades[-1]["timestamp"]
                since = last_trade_time + 1  # Avoid fetching the same trade again
                time.sleep(self.exchange.rateLimit / 1000)
            except Exception as e:
                print(f"Error fetching trades: {e}")
                break
        return all_trades

    def calculate_pnl(self, trades):
        """
        Calculate P&L from a list of trades.

        :param trades: A list of trade dictionaries.
        :return: The net P&L.
        """
        df = pd.DataFrame(trades)
        if df.empty:
            print("No trades found.")
            return None

        # Ensure numeric columns are of correct type
        df["cost"] = pd.to_numeric(df["cost"], errors="coerce").fillna(0.0)
        df["amount"] = pd.to_numeric(df["amount"], errors="coerce").fillna(0.0)

        # Extract fee information
        df["fee_cost"] = df["fee"].apply(lambda x: float(x["cost"]) if x else 0.0)
        df["fee_currency"] = df["fee"].apply(lambda x: x["currency"] if x else None)

        # Calculate total fees in quote currency
        total_fees = df[df["fee_currency"] == self.quote_currency]["fee_cost"].sum()

        # Calculate total buy and sell amounts
        total_buy = df[df["side"] == "buy"]["cost"].sum()
        total_sell = df[df["side"] == "sell"]["cost"].sum()

        # Calculate net P&L
        pnl = total_sell - total_buy - total_fees

        print("\n")
        print("=" * 50)
        print(f"Bot: {self.bot_name}")
        print(f"Exchange: {self.exchange_id}")
        print(f"Trading pair: {self.trading_pair}")
        print(
            f"from: {datetime.fromtimestamp(trades[0]['timestamp'] / 1000)}, {datetime.now().astimezone().tzinfo}"
        )
        print(
            f"to: {datetime.fromtimestamp(trades[-1]['timestamp'] / 1000)}, {datetime.now().astimezone().tzinfo}"
        )
        print("=" * 50)
        print(f"Total Buy: {total_buy:.8f} {self.quote_currency}")
        print(f"Total Sell: {total_sell:.8f} {self.quote_currency}")
        print(f"Total Fees: {total_fees:.8f} {self.quote_currency}")
        print(f"P&L: {pnl:.8f} {self.quote_currency}")

        return pnl

    def run(self, days=7):
        """
        Fetch trades and calculate P&L over the last 'days' days.

        :param days: Number of days to look back for trades (default 7 days).
        """
        since = self.exchange.parse8601(
            (datetime.utcnow() - timedelta(days=30)).isoformat()
        )
        until = self.exchange.parse8601(datetime.utcnow().isoformat())
        print(
            f"Fetching trades for {self.trading_pair} from {datetime.utcfromtimestamp(since / 1000)} to {datetime.utcfromtimestamp(until / 1000)}"
        )
        trades = self.fetch_trades(since=since, until=until)
        self.calculate_pnl(trades)


if __name__ == "__main__":
    # Prompt user for exchange ID
    exchange_id_input = input("Enter the exchange ID (e.g., binance): ").strip().lower()
    exchange_id = exchange_id_input if exchange_id_input else "binance"

    # Prompt user for trading pair
    trading_pair_input = (
        input("Enter the trading pair (e.g., BTC/USDT): ").strip().upper()
    )
    trading_pair = trading_pair_input if trading_pair_input else "BTC/USDT"

    # Prompt user for days to look back
    days_input = input("Enter the number of days to look back (default 7): ").strip()
    days = int(days_input) if days_input else 7

    # Initialize PnLCalculator
    calculator = PnLCalculator(
        exchange_id=exchange_id,
        trading_pair=trading_pair,
    )

    # Run the P&L calculation
    calculator.run(days=days)
