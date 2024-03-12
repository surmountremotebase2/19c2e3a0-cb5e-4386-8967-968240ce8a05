from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
        """
        Initialize the strategy with an empty list of candidate stocks.
        """
        self.candidate_stocks = []
        # Track entry prices for the stocks we invest in
        self.entry_prices = {}

    @property
    def assets(self):
        """
        Specify the list of assets this strategy will evaluate.
        """
        return self.candidate_stocks

    @property
    def interval(self):
        """
        Run this strategy on a minute interval.
        """
        return "1min"

    def run(self, data):
        """
        Executes the strategy to buy stocks that meet the criteria and sells based on the
        profit/loss threshold.
        """
        allocation_dict = {}
        
        # Populate candidate_stocks list at the beginning of the run function
        self.populate_candidate_stocks(data)

        for ticker in self.assets:
            ohlcv_data = data["ohlcv"][ticker]
            asset_data = Asset(ticker)
            
            # Criteria checks
            stock_price = ohlcv_data["close"][-1]
            stock_volume = ohlcv_data["volume"][-1]
            average_volume = sum(ohlcv_data["volume"][-10:]) / 10  # 10-day average volume
            percentage_change = ((stock_price - ohlcv_data["open"][-1]) / ohlcv_data["open"][-1]) * 100
            
            # Check for stock criteria: Price between 1 and 20, volume 500%+ average, less than 20M shares, 10%+ increase
            if 1 <= stock_price <= 20 and stock_volume >= 5 * average_volume and asset_data.outstandingShares < 20000000 and percentage_change > 10:
                allocation_dict[ticker] = 0.1  # Allocate a portion of the portfolio, e.g., 10%
                self.entry_prices[ticker] = stock_price  # Track entry price for sell criteria
            
            # Check sell criteria based on entry price if stock is already in the portfolio
            elif ticker in self.entry_prices:
                entry_price = self.entry_prices[ticker]
                if stock_price <= 0.99 * entry_price or stock_price >= 1.02 * entry_price:
                    allocation_dict[ticker] = 0  # Sell the stock
                    del self.entry_prices[ticker]  # Remove from the tracker once sold
                
                else:
                    # Hold if neither profit nor loss threshold is met
                    allocation_dict[ticker] = 0.1  # Maintain current allocation

        return TargetAllocation(allocation_dict)
    
    def populate_candidate_stocks(self, data):
        """
        Populate the candidate_stocks list based on some criteria.
        """
        # Example criteria: Include all assets with positive percentage change
        for ticker in data["ohlcv"]:
            ohlcv_data = data["ohlcv"][ticker]
            percentage_change = ((ohlcv_data["close"][-1] - ohlcv_data["open"][-1]) / ohlcv_data["open"][-1]) * 100
            if percentage_change > 0:
                self.candidate_stocks.append(ticker)