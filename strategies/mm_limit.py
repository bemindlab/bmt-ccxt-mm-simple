import ccxt
import logging
import json
import time


class LimitOrderMarketMaker:
    """Class for Limit Order Market Making with ccxt and multiple order levels."""

    def __init__(
        self,
        bot_name,
        config_path,
        base_order_amount=0,
        order_levels=3,
    ):
        logging.info("=" * 50)
        logging.info("Initializing Limit Order Market Maker bot...")
        logging.info("-" * 50)
        logging.info(f"Bot name: {bot_name}")
        logging.info(f"Base order amount: {base_order_amount}")
        logging.info(f"Order levels: {order_levels}")
        logging.info("=" * 50)

        self.bot_name = bot_name
        self.config = self.read_config(bot_name, config_path)
        self.base_order_amount = float(base_order_amount)
        self.order_levels = order_levels  # Number of levels

        # Set the maximum spread to 2% (0.02)
        self.max_spread = 0.02  # 2% total spread
        self.spread_per_level = self.max_spread / self.order_levels

        # Initialize exchange via ccxt
        self.exchange = self.initialize_exchange()
        self.trading_pair = self.config["bot"]["trading_pair"]

        self.base_asset = self.trading_pair.split("/")[0]  # e.g., TOAD
        self.quote_asset = self.trading_pair.split("/")[1]  # e.g., USDT

        # Store active orders
        self.active_orders = []

    def show_balance(self):
        balance = self.exchange.fetch_balance()
        logging.info(
            f"Current balance: {json.dumps(balance.get('total', {}), indent=2)}"
        )
        logging.info(
            f"Available balance: {json.dumps(balance.get('free', {}), indent=2)}"
        )

    def show_orders(self):
        open_orders = self.exchange.fetch_open_orders(self.trading_pair)
        logging.info(f"Open orders:")
        for order in open_orders:
            logging.info(
                f"{order['id']}: {order['side']} {order['amount']} @ {order['price']}"
            )

    def clear_orders(self):
        """Cancel all open orders."""
        try:
            open_orders = self.exchange.fetch_open_orders(self.trading_pair)
            for order in open_orders:
                self.exchange.cancel_order(order["id"], self.trading_pair)
                logging.info(f"Canceled order: {order['id']}")
            # Clear the active orders list
            self.active_orders = []
        except Exception as e:
            logging.error(f"Error canceling orders: {e}")

    def read_config(self, bot_name, config_path):
        """Read the exchange configuration from the config file."""
        try:
            with open(config_path, "r") as file:
                config = json.load(file)
            if bot_name in config.get("bots", {}):
                bot = config["bots"][bot_name]
                exchange = config["exchanges"][bot["exchange_set"]][bot["exchange"]]
                return dict(
                    bot=bot,
                    exchange=exchange,
                )
            else:
                logging.error(f"Bot '{bot_name}' not found in the config file.")
                raise Exception(f"Bot '{bot_name}' not found in the config file.")
        except FileNotFoundError:
            logging.error(f"Config file '{config_path}' not found.")
            raise Exception(f"Config file '{config_path}' not found.")
        except Exception as e:
            logging.error(f"Error reading config file: {e}")
            raise Exception(f"Error reading config file: {e}")

    def initialize_exchange(self):
        """Initialize the exchange dynamically based on the exchange name."""
        try:
            exchange_name = self.config["bot"]["exchange"]
            config = self.config["exchange"]
            exchange_class = getattr(ccxt, self.config["bot"]["exchange"])
            exchange = exchange_class(
                {
                    "apiKey": config["api_key"],
                    "secret": config["api_secret"],
                    "password": config.get("api_password", None),
                    "enableRateLimit": True,
                }
            )
            logging.info(f"Initialized exchange: {exchange_name}")
            return exchange
        except AttributeError:
            logging.error(f"Exchange '{exchange_name}' is not supported by CCXT.")
            raise Exception(f"Exchange '{exchange_name}' is not supported by CCXT.")
        except Exception as e:
            logging.error(f"Error initializing exchange: {e}")
            raise Exception(f"Error initializing exchange: {e}")

    def get_market_data(self):
        ticker = self.exchange.fetch_ticker(self.trading_pair)
        mid_price = (ticker["bid"] + ticker["ask"]) / 2
        return mid_price

    def fetch_balances(self):
        # Fetch the balance from the exchange
        balance = self.exchange.fetch_balance()
        base_balance = balance[self.base_asset]["free"]  # Free balance of base asset
        quote_balance = balance[self.quote_asset]["free"]  # Free balance of quote asset
        return base_balance, quote_balance

    def place_limit_orders(self):
        mid_price = self.get_market_data()

        # Calculate the spread per level to stay within ±2%
        spread_per_level = self.max_spread / self.order_levels

        # Before placing orders, calculate total required balances
        total_buy_amount = 0
        total_sell_amount = 0

        # Lists to store orders to be placed
        buy_orders = []
        sell_orders = []

        base_balance, quote_balance = self.fetch_balances()

        # Calculate order amounts and prices
        for level in range(1, self.order_levels + 1):
            # Calculate price for each buy and sell level within ±2%
            level_spread = spread_per_level * level
            buy_price = mid_price * (1 - level_spread)
            sell_price = mid_price * (1 + level_spread)

            # Use base_order_amount per order
            buy_order_amount = self.base_order_amount
            sell_order_amount = self.base_order_amount

            total_buy_amount += buy_order_amount * buy_price  # in quote currency
            total_sell_amount += sell_order_amount  # in base currency

            # Store the orders to place later
            buy_orders.append((buy_order_amount, buy_price))
            sell_orders.append((sell_order_amount, sell_price))

        # Check if we have sufficient balances
        if total_buy_amount > quote_balance:
            logging.warning("Insufficient quote balance to place all buy orders.")
            scaling_factor = quote_balance / total_buy_amount
            buy_orders = [
                (amount * scaling_factor, price) for amount, price in buy_orders
            ]
            logging.info(
                f"Adjusted buy order amounts by scaling factor {scaling_factor:.2f}"
            )

        if total_sell_amount > base_balance:
            logging.warning("Insufficient base balance to place all sell orders.")
            scaling_factor = base_balance / total_sell_amount
            sell_orders = [
                (amount * scaling_factor, price) for amount, price in sell_orders
            ]
            logging.info(
                f"Adjusted sell order amounts by scaling factor {scaling_factor:.2f}"
            )

        # Place buy orders
        for level, (buy_order_amount, buy_price) in enumerate(buy_orders, 1):
            if buy_order_amount <= 0:
                continue  # Skip zero or negative amounts
            try:
                buy_order = self.exchange.create_limit_buy_order(
                    self.trading_pair, buy_order_amount, buy_price
                )
                self.active_orders.append(buy_order)  # Track the buy order
                logging.info(
                    f"Placed buy order at level {level}: {buy_order.get('id')} amount: {buy_order_amount:.6f} price: {buy_price:.6f}"
                )
            except Exception as e:
                logging.error(f"Failed to place buy order at level {level}: {e}")

        # Place sell orders
        for level, (sell_order_amount, sell_price) in enumerate(sell_orders, 1):
            if sell_order_amount <= 0:
                continue  # Skip zero or negative amounts
            try:
                sell_order = self.exchange.create_limit_sell_order(
                    self.trading_pair, sell_order_amount, sell_price
                )
                self.active_orders.append(sell_order)  # Track the sell order
                logging.info(
                    f"Placed sell order at level {level}: {sell_order.get('id')} amount: {sell_order_amount:.6f} price: {sell_price:.6f}"
                )
            except Exception as e:
                logging.error(f"Failed to place sell order at level {level}: {e}")

    def check_and_replace_orders(self):
        # Fetch open orders from the exchange
        open_orders = self.exchange.fetch_open_orders(self.trading_pair)
        open_order_ids = [order["id"] for order in open_orders]

        # Remove orders that are no longer open from active_orders
        self.active_orders = [
            order for order in self.active_orders if order["id"] in open_order_ids
        ]

        # If any orders have been filled or canceled, replace them
        if len(self.active_orders) < self.order_levels * 2:
            logging.info("Some orders have been filled or canceled. Replacing orders.")
            # Clear remaining orders before placing new ones
            self.clear_orders()
            self.place_limit_orders()

    def run(self):
        while True:
            try:
                if not self.active_orders:
                    self.place_limit_orders()  # Place initial orders if none exist

                # Check and replace orders
                self.check_and_replace_orders()
                time.sleep(30)  # Adjust timing as needed
                logging.info("=" * 50)
                logging.info("Running next iteration...\n")
            except Exception as e:
                logging.error(f"Error in running bot: {e}")
                time.sleep(30)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    logging.info("=" * 50)
    token = input("Enter the token: ")
    logging.info("-" * 50)
    config_path = f"configs/{token}_bots.json"

    try:
        config = json.load(open(config_path, "r"))
    except FileNotFoundError:
        logging.error(f"Config file '{config_path}' not found.")
        exit()

    if token not in config.get("token", None):
        logging.error(f"Token '{token}' not found in the config file.")
        exit()

    bot_name = None

    # Display the list with indices
    bot_names = []
    for i, name in enumerate(config["bots"].keys()):
        bot_names.append(name)
        logging.info(f"{i+1}: {name}")
    logging.info("=" * 50)

    # Ask for user input (index)
    try:
        index = int(input("Enter the index of the bot you're looking for: ")) - 1
        # Check if the index is within the range of the list
        if 0 <= index < len(bot_names):
            logging.info(f"You selected: {bot_names[index]}\n")
            bot_name = bot_names[index]
        else:
            logging.error("Index out of range.")
            exit()
    except ValueError:
        logging.error("Please enter a valid integer for the index.")
        exit()

    # Initialize the bot
    bot = LimitOrderMarketMaker(
        bot_name,
        config_path,
    )

    # Ask for user input to show balance
    show_balance = input("Do you want to show balance? (y/n): ")
    if show_balance.lower() == "y":
        bot.show_balance()
        logging.info("=" * 50 + "\n")

    # Ask for user input to show open orders
    show_orders = input("Do you want to show open orders? (y/n): ")
    if show_orders.lower() == "y":
        bot.show_orders()
        logging.info("=" * 50 + "\n")

    clear_orders = input("Do you want to clear all open orders? (y/n): ")
    if clear_orders.lower() == "y":
        bot.clear_orders()
        logging.info("=" * 50 + "\n")

    # Run the bot or exit
    run_bot = input("Do you want to run the bot? (y/n): ")
    if run_bot.lower() == "n":
        exit()

    # Ask for the base order amount
    try:
        order_amount = float(input("Enter the base order amount: "))
        if order_amount <= 0:
            logging.error("The order amount must be greater than 0.")
            exit()
    except ValueError:
        logging.error("Please enter a valid number for the order amount.")
        exit()

    # Ask for the number of order levels
    try:
        order_levels = int(input("Enter the number of order levels (max 10): "))
        if order_levels <= 0 or order_levels > 10:
            logging.error("The number of order levels must be between 1 and 10.")
            exit()
    except ValueError:
        logging.error("Please enter a valid integer for the number of order levels.")
        exit()

    # Update the bot with user-provided parameters
    bot.base_order_amount = order_amount
    bot.order_levels = order_levels
    bot.spread_per_level = bot.max_spread / bot.order_levels

    # Run the bot
    bot.run()
