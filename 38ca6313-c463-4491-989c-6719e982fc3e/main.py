from surmount.base_class import Strategy, TargetAllocation
from surmount.data import ohlcv
import pandas_ta as ta
import pandas as pd

class TradingStrategy(Strategy):
    def __init__(self):
        # Initialize your strategy and define your targeted tickers here
        self.tickers = ["AAPL", "MSFT", "GOOGL", "AMZN"]  # Example tickers
        # No specific data list initialization required for this strategy in this example
    
    @property
    def interval(self):
        # Use daily data for calculating the 30-day average volume
        return "1day"
    
    @property
    def assets(self):
        # This specifies which assets we're interested in trading
        return self.tickers
    
    @property
    def data(self):
        # This would return any additional data sources required; 
        # for this strategy example, we are not using any extra data sources.
        return []

    def run(self, data):
        # Initialize allocation with no positions as we determine which stocks to trade
        allocation_dict = {ticker: 0 for ticker in self.tickers}

        for ticker in self.tickers:
            # Ensure there is sufficient data for calculating averages
            if len(data["ohlcv"][ticker]) >= 30:
                # Calculate the 30-day average volume
                avg_volume = ta.sma(pd.Series([i[ticker]["volume"] for i in data["ohlcv"]]), length=30)[-1]
                current_volume = data["ohlcv"][-1][ticker]["volume"]

                # Check if the current volume is at least 50% higher than the 30-day average
                if current_volume > 1.5 * avg_volume:
                    # If condition met, set allocation for this stock to a value (e.g., 0.25)
                    # This assumes equal distribution among selected tickers for simplicity
                    # Adjust strategy based on your risk and capital management
                    allocation_dict[ticker] = 1 / len(self.tickers)
        
        # Return the target allocation
        return TargetAllocation(allocation_dict)