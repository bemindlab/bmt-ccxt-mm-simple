import ccxt
import logging
import json


def load_config(config_path):
    """Read the exchange configuration from the config file."""
    try:
        with open(config_path, "r") as file:
            config = json.load(file)
        if config:
            return config.get("bots", {})
        else:
            logging.error(f"Config file '{config_path}' is empty.")
            raise Exception(f"Config file '{config_path}' is empty.")
    except FileNotFoundError:
        logging.error(f"Config file '{config_path}' not found.")
        raise Exception(f"Config file '{config_path}' not found.")


def load_config_with_bot_name(bot_name, config_path):
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


def initialize_exchange(config):
    """Initialize the exchange dynamically based on the exchange name."""
    try:
        exchange_name = config["bot"]["exchange"]
        config = config["exchange"]
        exchange_class = getattr(ccxt, exchange_name)
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
