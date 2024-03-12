from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset

class TradingStrategy(Strategy):
    @property
    def assets(self):
        """
        Specify the list of assets this strategy will evaluate.
        """
        return ["ADD","AMBO","AMIX","APVO","AUUD","AVGR","AZTR","BBLG","BIAF","BOF","BPTH","BSGM","BTCY","BTOG","CAUD","CISO","DLA","EEIQ","EFOI","WAVD","TNON","STI","STAF","SOND","SNCR","RELI","RCRT","PRTG","PIK","OMQS","NXL","NUKK","LBBB","KA","JAN","INSG","IDAI","HWH","HEPA","HTCI","GXAI","EZFL","EGIO","EFOIEEIQ","DLA","CMAX"]

    @property
    def interval(self):
        """
        Run this strategy on a minute interval.
        """
        return "1min"

    def run(self, data):
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