# Basic Market Making Strategy
This is a basic market making strategy that I have implemented in Python. The strategy is based on the following assumptions:

## Assumptions
1. The market is a two-sided market with a bid and an ask price.
2. target_spread is the desired spread between the bid and ask price.
3. The bid and ask prices are updated every time a new order is placed.
4. The bid and ask prices are updated by adding or subtracting the spread from the mid price.
5. Tradind depth is the number of orders that can be placed on the bid and ask side of the market.

## Strategy
1. LimitOrderMarketMaker class is used to implement the market making strategy.
- The class has the following attributes:
  - bot_name: The name of the bot.
  - config_path: The path to the configuration file.
  - base_order_amount: The base amount of the order.
  - order_levels: The number of orders that can be placed on the bid and ask side of the market.
  - trading_depth: The number of orders that can be placed on the bid and ask side of the market.
  - max_spread: The maximum spread between the bid and ask price.
  - spread_per_level: The spread per level.


## Configuration File
The configuration file is a JSON file that contains the following parameters:
- token: The token of the bot.
- bot_name: The name of the bot.
  - base_order_amount: The base amount of the order.
  - ...

```json
{
    "token": "btc",
    "bots": {
        "Strategy1": {
            "bot_name": "Strategy1",
            "exchange_set": "set1",
            "exchange": "binance",
            "trading_pair": "TOAD/USDT",
            "parameters": {
                "desired_depth_per_side": 10000,
                "order_levels": 3
            }
        },
    },
    "exchanges": {
        "set1": {
            "exchange": "binance",
            "api_key": "API_KEY",
            "api_secret": "API_SECRET"
        }
    }
}
```

Copy the bot_example.json it in a file named {token}_bots.json. Replace the API_KEY and API_SECRET with your binance API key and secret.
``` bash
cp bot_example.json btc_bots.json
```

## Installation
``` bash
python3 -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

## Usage
``` bash
python main.py
```