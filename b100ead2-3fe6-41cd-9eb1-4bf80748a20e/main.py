from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["AAPL", "GOOGL", "MSFT", "AMZN","ABT","AMD","NVDA","HD"]
        # Initialize a dictionary to track the holding status of each stock
        self.stock_holdings = {ticker: False for ticker in self.tickers}

    @property
    def interval(self):
        # Using daily interval for checking the price gain over 3 days
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}
        
        for ticker in self.tickers:
            # Check if we have enough data points (at least 4 days to make a decision)
            if len(data["ohlcv"]) < 4:
                allocation_dict[ticker] = 0
                continue
            
            ohlcv_data = data["ohlcv"]
            
            # Check if the stock has been gaining for 3 consecutive days
            gaining_for_5_days = ohlcv_data[-6][ticker]["close"] < ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-5][ticker]["close"] < ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-4][ticker]["close"] < ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-3][ticker]["close"] < ohlcv_data[-2][ticker]["close"] and \
                                 ohlcv_data[-2][ticker]["close"] < ohlcv_data[-1][ticker]["close"]

            losing_for_5_days =  ohlcv_data[-6][ticker]["close"] > ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-5][ticker]["close"] > ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-4][ticker]["close"] > ohlcv_data[-3][ticker]["close"] and \
                                 ohlcv_data[-3][ticker]["close"] > ohlcv_data[-2][ticker]["close"] and \
                                 ohlcv_data[-2][ticker]["close"] > ohlcv_data[-1][ticker]["close"]
            
            # If the stock is currently being held, sell it (set allocation to 0) no matter what
            if self.stock_holdings[ticker]:
                allocation_dict[ticker] = 0
                self.stock_holdings[ticker] = False  # Update the holding status
            # If the stock has been gaining for 3 days and it's not currently held, buy it
            elif gaining_for_5_days:
                allocation_dict[ticker] = 1  # Allocate all to this stock
                self.stock_holdings[ticker] = True  # Update the holding status
            elif losing_for_5_days:
                allocation_dict[ticker] = 1  # Allocate all to this stock
                self.stock_holdings[ticker] = True  # Update the holding status
            else:
                allocation_dict[ticker] = 0  # Do not allocate if the condition doesn't meet
        
        # Return the target allocation
        return TargetAllocation(allocation_dict)