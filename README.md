# Basic Market Making Strategy
This is a basic market making strategy that I have implemented in Python. The strategy is based on the following assumptions:

## Assumptions
1. The market is a two-sided market with a bid and an ask price.
2. target_spread is the desired spread between the bid and ask price.
3. The bid and ask prices are updated every time a new order is placed.
4. The bid and ask prices are updated by adding or subtracting the spread from the mid price.
5. Tradind depth is the number of orders that can be placed on the bid and ask side of the market.

## Strategy
1. TradingDepthStrategy class is used to implement the market making strategy.
- The class has the following attributes:
  - bot_name: The name of the bot.
  - config_path: The path to the configuration file.
  - base_order_amount: The base amount of the order.
  - order_levels: The number of orders that can be placed on the bid and ask side of the market.
  - depth: The number of orders that can be placed on the bid and ask side of the market.
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
            "trading_pair": "BTC/USDT",
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
run the following command to run the bot
``` bash
python3 strategies/depth.py
```

## Usage Docker Compose
run the following command to build and run the docker container
``` bash
docker-compose up --build
```

Or in detached mode
``` bash
docker-compose up -d
```

## GKE (Google Kubernetes Engine) deployment
steps to deploy the trading bot on GKE

### Build the docker image
``` bash
export PROJECT_ID=your-project-id
export PROJECT_ZONE=your-project-zone
export NAMESPACE=your-namespace
```

### Copy config files
``` bash
cp bot_example.json btc_bots.json
cp kube_deploy_example kube_deoploy
```

### build the docker image and  push the docker image to GCR
``` bash
gcloud auth configure-docker
gcloud builds submit --tag gcr.io/$PROJECT_ID/tradingbot
docker push gcr.io/$PROJECT_ID/tradingbot
```

### Create a GKE cluster
``` bash
gcloud container clusters create market-maker-cluster --num-nodes=1 --zone=$PROJECT_ZONE
kubectl create namespace $NAMESPACE
kubectl create deployment tradingbot-deployment --image=gcr.io/$PROJECT_ID/tradingbot:lastest -n $NAMESPACE
```

### ssh into the pod
``` bash
kubectl exec -it tradingbot-deployment -- /bin/bash
```

### get deployment 
``` bash
kubectl get pods
kubectl get deployments
kubectl get services
```

### delete deployment
``` bash
kubectl delete deployment tradingbot-deployment
kubectl delete service tradingbot-service
```

### delete cluster
``` bash
gcloud container clusters delete market-maker-cluster --zone=$PROJECT_ZONE
```

### delete namespace
``` bash
kubectl delete namespace $NAMESPACE

### delete project
``` bash
gcloud projects delete $PROJECT_ID
```