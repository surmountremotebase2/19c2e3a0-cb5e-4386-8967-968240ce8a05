from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, OHLCV

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker of interest
        self.tickers = ["TSLA"]

    @property
    def interval(self):
        # The interval at which the strategy will operate
        return "1day"

    @property
    def assets(self):
        # The assets that this strategy will consider
        return self.tickers

    @property
    def data(self):
        # Define the data needed for this strategy. In this case, historical OHLCV data for TSLA.
        return [OHLCV(ticker) for ticker in self.tickers]

    def run(self, data):
        # Initialize the allocation dictionary
        allocation_dict = {"TSLA": 0}

        if "TSLA" in data["ohlcv"]:
            tsla_ohlcv = data["ohlcv"]["TSLA"]
            # Make sure we have at least two data points to compare
            if len(tsla_ohlcv) > 1:
                # Get the closing price of the last two days
                previous_close = tsla_ohlcv[-2]["close"]
                current_close = tsla_ohlcv[-1]["close"]

                # Check if there was a significant drop in price which could indicate a large sell order
                # The threshold for "significant" can be adjusted. Here, it's arbitrarily set to a 5% decrease.
                if (previous_close - current_close) / previous_close >= 0.05:
                    log("Large sell detected for TSLA. Buying 1 share.")
                    # Buy 1 share of TSLA. The actual mechanics of specifying "1 share" might depend on
                    # how the Surmount trading platform interprets allocation values.
                    # This allocation may need adjustment based on account size,
                    # a fixed fractional allocation, or another method to fit actual trading.
                    allocation_dict["TSLA"] = 1  # This assumes allocation is interpreted as a number of shares

        # Return the target allocation. This might need to be normalized or adjusted depending
        # on the platform's requirements for order sizing.
        return TargetAllocation(allocation_dict)