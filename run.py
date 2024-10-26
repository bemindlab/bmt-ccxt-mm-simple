import json
import logging

from market.pnl import PnLCalculator
from utils.config import load_config
from utils.user_input import (
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
    print("-" * 50)

    # get the feature menu
    choice = get_feature_menu()
    print(f"Selected feature: {choice}")

    # handle the user's choice
    while True:
        if choice == "1":
            # Prompt user for days to look back
            days_input = input(
                "Enter the number of days to look back (default 7): "
            ).strip()
            days = int(days_input) if days_input else 7

            pnl = PnLCalculator()
            pnl.initialize_bot(selected_bot, bot_config_path)
            pnl.run(days)

            print("-" * 50, "\n")
            exit()
        elif choice == "2":
            # buy and sell on market price
            exit()
        else:
            print("Exiting...")
            exit()
