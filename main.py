import logging

if __name__ == "__main__":
    # initialize logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(message)s",
        handlers=[
            logging.FileHandler("tradingbot.log"),
            logging.StreamHandler(),
        ],
    )
    print("Hello my bot!")

    # initialize strategies
    # ----------------
    # market_making_limit = MarketMakingLimit()

    # run strategies
    # ----------------
    # swing_trading.run()
    # market_making_limit.run()
