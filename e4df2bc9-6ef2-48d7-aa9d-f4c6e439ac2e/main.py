from surmount.base_class import Strategy, TargetAllocation
from surmount.data import Asset
from surmount.logging import log

class TradingStrategy(Strategy):
    def __init__(self):
        # Assuming 'small_cap_stocks' is a dynamic list updated with small cap stocks.
        # In reality, you would need a process that updates this list regularly based on market cap data.
        self.small_cap_stocks = ["MSFT", "AAPL"]  # Placeholder tickers.
        self.selected_stock = None
        self.entry_price = None
        self.target_gain = 0.10  # 10% gain target

    @property
    def interval(self):
        return "1day"

    @property
    def assets(self):
        # Return only the selected stock if one is being held, otherwise return the small cap list
        return [self.selected_stock] if self.selected_stock else self.small_cap_stocks

    @property
    def data(self):
        # Request both OHLCV and the financials for potential or current stocks
        data_requests = [OHLCV(ticker) for ticker in self.assets]
        data_requests += [CompanyFinancials(ticker) for ticker in self.assets]
        return data_requests

    def run(self, data):
        # Placeholder for the allocation decision
        allocation_dict = {ticker: 0 for ticker in self.small_cap_stocks}

        if self.selected_stock:
            # Check if the selected stock has achieved the target gain
            current_price = data[OHLCV(self.selected_stock)].close[-1]
            if self.entry_price:
                gain = (current_price - self.entry_price) / self.entry_price
                if gain >= self.target_gain:
                    # Sell the stock
                    log(f"Selling {self.selected_stock} after {100 * gain:.2f}% gain.")
                    self.selected_stock = None
                    return TargetAllocation(allocation_dict)
            # Keep holding if target not achieved
            allocation_dict[self.selected_stock] = 1
        else:
            # Find a new stock with no debt
            for ticker in self.small_cap_stocks:
                financials = data[CompanyFinancials(ticker)]
                if financials.debt == 0:
                    # Buy a no-debt small cap stock
                    log(f"Buying {ticker} with no debt.")
                    self.selected_stock = ticker
                    self.entry_price = data[OHLCV(ticker)].close[-1]
                    allocation_dict[ticker] = 1
                    break

        return TargetAllocation(allocation_dict)