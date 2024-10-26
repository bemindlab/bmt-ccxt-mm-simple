import os
import logging

from utils.config import load_config


def get_bots_config_names():
    """Get the list of bot names from the configs directory."""
    bot_names = []
    try:
        for file in os.listdir("configs"):
            if file.endswith(".json") and file != "config.json":
                bot_names.append(file.split(".")[0])
    except Exception as e:
        logging.error(f"Error getting bot names: {e}")
    return bot_names


def get_slected_bot_config_path():
    # load the bot names
    bot_config_names = get_bots_config_names()
    print("Available configs:")
    print("-" * 50)
    for i, name in enumerate(bot_config_names):
        print(f"{i+1}. {name}")

    # get the selected bot config
    print("-" * 50)
    name_no = int(input("Select a bot config no: "))
    name = bot_config_names[name_no - 1]
    bot_config_path = f"configs/{name}.json"
    print(f"Loading bot configuration from {bot_config_path}")
    print("-" * 50)
    return bot_config_path


def get_slected_bot_names(config_path):
    """Get the list of bot names from the config file."""
    bots = load_config(config_path)
    if bots is None or len(bots.keys()) == 0:
        raise Exception("No bots found in the config file.")

    print("Available bots:")
    print("-" * 50)
    for i, bot_name in enumerate(bots.keys()):
        print(f"{i+1}. {bot_name}")
    selected = int(input("Select a bot: "))

    if selected < 1 or selected > len(bots.keys()):
        raise Exception("Invalid bot selection.")

    return list(bots.keys())[selected - 1]


def get_feature_menu():
    """Print the feature menu and return the user's choice."""
    print("Select a feature:")
    print("-" * 50)
    menu_names = ["Balance","PnL Calculator","History", "Exit"]
    for i, name in enumerate(menu_names):
        print(f"{i+1}. {name}")

    print("Exit")
    choice = input("Enter your choice no: ")
    return choice


def get_strategy_menu():
    """Print the strategy menu and return the user's choice."""
    print("Select a strategy:")
    print("1. Depth Trading Strategy")
    print("2. Exit")
    choice = input("Enter your choice (1/2): ")
    return choice


def get_exchange_id():
    """Get the exchange ID from the user."""
    exchange_id = input("Enter the exchange ID (e.g., binance): ").strip().lower()
    return exchange_id if exchange_id else "binance"


def get_trading_pair():
    """Get the trading pair from the user."""
    trading_pair = input("Enter the trading pair (e.g., BTC/USDT): ").strip().upper()
    return trading_pair if trading_pair else "BTC/USDT"


def get_days():
    """Get the number of days to look back from the user."""
    days = input("Enter the number of days to look back (default 7): ").strip()
    return int(days) if days else 7
