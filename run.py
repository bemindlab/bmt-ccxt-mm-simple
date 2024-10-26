from time import sleep
import logging
import random

from src.history.pnl import PnLCalculator
from src.strategies.market import MarketPriceStrategy
from src.utils.user_input import (
    get_feature_menu,
    get_slected_bot_config_path,
    get_slected_bot_names,
)

if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    print("=" * 50)
    print("Welcome to the Crypto Trading Bot!")
    print("=" * 50)
    bot_config_path = get_slected_bot_config_path()

    # load the selected bot config
    selected_bot = get_slected_bot_names(bot_config_path)
    print(f"Selected bot: {selected_bot}")
    print("-" * 50, "\n")

    # get the feature menu
    print("-" * 50, "\n")
    choice = get_feature_menu()
    print(f"Selected feature: {choice}")

    # handle the user's choice
    while True:
        #  market price strategy
        if choice == "1":
            print("-" * 50, "\n")
            exit()

        elif choice == "2":
            # Prompt user for days to look back
            print("-" * 50, "\n")
            days_input = input(
                "Enter the number of days to look back (default 7): "
            ).strip()
            days = int(days_input) if days_input else 7

            pnl = PnLCalculator()
            pnl.initialize_bot(selected_bot, bot_config_path)
            pnl.run(days)

            print("-" * 50, "\n")
            exit()
        elif choice == "4":
            # buy and sell on market price
            print("-" * 50, "\n")
            order_amount = input("Enter the order amount: ")
            order_amount = float(order_amount)
            if order_amount <= 0:
                print("Order amount must be greater than 0")
                exit()

            target_volume = input("Enter the target volume: ")
            target_volume = float(target_volume)
            if target_volume <= 0:
                print("Target volume must be greater than 0")
                exit()

            strategy = MarketPriceStrategy()
            strategy.initialize_bot(
                selected_bot, bot_config_path, order_amount, target_volume
            )
            while True:
                strategy.execute()
                sleep(random.randint(30, 60))
        else:
            print("Exiting...")
            exit()
