import ccxt
import logging
import json
import time


class OrderBookUtils:
    """Class for Limit Order Market Making with ccxt and multiple order levels."""

    def __init__(
        self,
        bot_name,
        config_path,
        base_order_amount=0,
        spread=0.02,
        order_levels=3,
        level_spread=0.5,
    ):

        print("=" * 50)
        print("Initializing Limit Order Market Maker bot...")
        print("-" * 50)
        print(f"Bot name: {bot_name}")
        print(f"Base order amount: {base_order_amount}")
        print(f"Spread: {spread}")
        print(f"Order levels: {order_levels}")
        print(f"Level spread: {level_spread}")
        print("=" * 50)

        self.bot_name = bot_name
        self.config = self.read_config(bot_name, config_path)
        self.base_order_amount = float(base_order_amount)
        self.spread = spread
        self.order_levels = order_levels  # Number of levels
        self.level_spread = level_spread  # Spread between levels

        # Initialize exchange via ccxt
        self.exchange = self.initialize_exchange()
        self.trading_pair = self.config["bot"]["trading_pair"]

        self.base_asset = self.trading_pair.split("/")[0]  # e.g., TOAD
        self.quote_asset = self.trading_pair.split("/")[1]  # e.g., USDT

        # Store active orders
        self.orders = []
        self.active_orders = []

    def read_config(self, bot_name, config_path):
        """Read the exchange configuration from exchanges.json."""
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
                logging.error(f"Exchange '{bot_name}' not found in the config file.")
                raise Exception(f"Exchange '{bot_name}' not found in the config file.")
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

    def show_balance(self):
        balance = self.exchange.fetch_balance()
        print("=" * 50)
        print(f"Balance for {self.bot_name}:")
        print(f"Current: {json.dumps(balance.get('total', {}), indent=2)}")
        print(f"Used: {json.dumps(balance.get('used', {}), indent=2)}")
        print(f"Available: {json.dumps(balance.get('free', {}), indent=2)}")

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
        except Exception as e:
            logging.error(f"Error canceling orders: {e}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)

    print("=" * 50)
    token = input("Enter the token: ")
    print("-" * 50)
    config_path = f"configs/{token}_bots.json"

    config = json.load(open(config_path, "r"))

    if token not in config.get("token", None):
        print(f"Token '{token}' not found in the config file.")
        exit()

    bot_name = None

    # Display the list with indices
    bot_names = []
    for i, name in enumerate(config["bots"].keys()):
        bot_names.append(name)
        print(f"{i+1}: {name}")
    print("=" * 50)

    # Ask for user input (index)
    try:
        index = int(input("Enter the index of the name you're looking for: ")) - 1
        # Check if the index is within the range of the list
        if 0 <= index < len(bot_names):
            print(f"You selected: {bot_names[index]}", "\n")
            bot_name = bot_names[index]
        else:
            print("Index out of range.")
    except ValueError:
        print("Please enter a valid integer for the index.")

    while True:
        bot = OrderBookUtils(
            bot_name,
            config_path,
        )
        bot.show_orders()
        print("=" * 50, "\n")

        bot.show_balance()
        print("=" * 50, "\n")

        # Ask for user input to show open orders
        # show_orders = input("Do you want to show open orders? (y/n): ")
        # if show_orders.lower() == "n":
        #     break
        time.sleep(20)

    exit()
