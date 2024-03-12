from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import BB, SMA
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership, InsiderTrading

class TradingStrategy(Strategy):
    def __init__(self):
        self.tickers = ["SQ"]
        # No additional data required for this strategy, hence empty list
        self.data_list = []
    
    @property
    def interval(self):
        # Using daily data for this strategy
        return "1day"
    
    @property
    def assets(self):
        # Strategy focuses only on Square (SQ)
        return self.tickers
    
    @property
    def data(self):
        # No additional data sources needed
        return self.data_list

    def run(self, data):
        ohlcv_data = data["ohlcv"]
        allocation = {}
        
        # Check if there's enough data for Bollinger Bands calculation (typically requires at least 20 periods)
        if len(ohlcv_data) >= 20:
            # Bollinger Bands indicator for SQ, with a 20-day period and standard deviation of 2 (default values)
            bb = BB("SQ", ohlcv_data, 20, 2)
            current_price = ohlcv_data[-1]["SQ"]["close"]
            
            # Determine the strategy for returning TargetAllocation
            # If the current price is above the upper Bollinger Band, allocate 100% to SQ
            if current_price > bb["upper"][-1]:
                log("Price above upper band, buying SQ")
                allocation["SQ"] = 1.0
            # If the current price is back to the mid Bollinger Band, reduce the position to 0, indicating a sell
            elif current_price <= bb["mid"][-1] and current_price > bb["lower"][-1]:
                log("Price returned to middle band, selling SQ")
                allocation["SQ"] = 0
            else:
                # Maintain the current allocation if no conditions are met
                log("No action required, holding position")
                allocation["SQ"] = 0
        
        return TargetAllocation(allocation)