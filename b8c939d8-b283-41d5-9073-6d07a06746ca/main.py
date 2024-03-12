from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership, InsiderTrading

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker of interest
        self.ticker = "MSFT"
        self.lookback_periods = 30  # Lookback period to calculate average volume
        self.large_sell_threshold = 10000  # Define what is considered a large sell order
        self.buy_signal_activated = False  # Track if a buy signal has been activated

    @property
    def assets(self):
        # Only interested in trading MSFT for this strategy
        return [self.ticker]

    @property
    def interval(self):
        # Strategy operates on 1-minute intervals
        return "1hour"

    def run(self, data):
        # Initialize positions with no holdings
        allocation_dict = {self.ticker: 0}
        
        # Extract the recent volume and trading data for MSFT
        recent_data = data["ohlcv"]
       
        # Calculate the average volume over the lookback period
        average_volume = sum([i[self.ticker]["volume"] for i in recent_data[-self.lookback_periods:]]) / self.lookback_periods
        current_volume = recent_data[-1][self.ticker]["volume"]
        transaction_type = recent_data[-1][self.ticker].get("acquisitionOrDisposition", "")
        transaction_amt = recent_data[-1][self.ticker].get("securitiesTransacted","")

        # If the current volume is significantly higher than the average, buy MSFT
        if current_volume > average_volume and not self.buy_signal_activated:
            log(f"Buy signal activated for {self.ticker} due to high volume")
            allocation_dict[self.ticker] = 1  # Buy (go long on) MSFT
            self.buy_signal_activated = True
        # Sell MSFT if a large sell order is detected
        elif self.buy_signal_activated and transaction_type == "D" and transaction_amt > self.large_sell_threshold:
            log(f"Sell signal activated for {self.ticker} due to large sell order")
            allocation_dict[self.ticker] = 0  # Sell MSFT
            self.buy_signal_activated = False
        # Continue holding MSFT if neither condition is met but a buy was previously activated
        elif self.buy_signal_activated:
            allocation_dict[self.ticker] = 1  # Maintain current holding

        return TargetAllocation(allocation_dict)