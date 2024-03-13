from surmount.base_class import Strategy, TargetAllocation
import numpy as np

class TradingStrategy(Strategy):
    def __init__(self):
        # Adjust these tickers as needed
        self.all_tickers = ["AAPL", "MSFT", "GOOGL", "AMZN", "FB", "BRK.B", "JNJ", "V", "PG", "UNH",
                            "JPM", "NVDA", "HD", "MA", "DIS", "PYPL", "BAC", "ADBE", "CMCSA", "XOM",
                            "NFLX", "TSLA", "KO", "PFE", "CSCO", "ABT", "PEP", "CVX", "ABBV", "MRK"]
        self.selected_tickers = []
        self.week_count = 0
        self.sell_phase = False

    @property
    def assets(self):
        # Dynamic asset list based on the current phase (buy/sell)
        return self.selected_tickers if self.sell_phase else self.all_tickers

    @property
    def interval(self):
        # Operates on a weekly interval
        return "1week"

    @property
    def data(self):
        # No additional data required for this strategy
        return []

    def run(self, data):
        allocation_dict = {}
        
        # If it's time to sell the selected tickers
        if self.sell_phase:
            for ticker in self.selected_tickers:
                allocation_dict[ticker] = 0  # Sell (set allocation to 0)
            self.selected_tickers = []  # Clear the list for the next batch
            self.sell_phase = False  # Next phase will be buying
        else:
            # Choose 10 random tickers from the list
            self.selected_tickers = np.random.choice(self.all_tickers, 10, replace=False).tolist()
            # Allocate evenly across the selected tickers
            for ticker in self.selected_tickers:
                allocation_dict[ticker] = 1 / len(self.selected_tickers)
            self.sell_phase = True  # Next phase will be selling

        return TargetAllocation(allocation_dict)