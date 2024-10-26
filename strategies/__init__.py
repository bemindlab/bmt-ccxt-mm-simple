# __init__.py inside 'strategies' folder

# Import the main classes or functions from your strategy modules
from .depth import TradingDepthStrategy

# Define what gets imported when someone does 'from strategies import *'
__all__ = ["TradingDepthStrategy"]
