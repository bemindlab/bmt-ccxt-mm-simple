from datetime import datetime, timedelta
import logging
import os
import json

from flask import Flask, jsonify, request

app = Flask(__name__)


@app.route("/healthcheck", methods=["GET"])
def healthcheck():
    return jsonify({"status": "healthy"}), 200


# TODO: Implement the strategy setup
# Eg. POST /strategies/default


@app.route("/strategies/depth", methods=["GET"])
def run_trading_depth():
    # TODO: Implement the trading strategy
    return jsonify({"status": "healthy"}), 200


if __name__ == "__main__":
    # Set up logging
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    app.run(host="0.0.0.0", port=3000, debug=True)
