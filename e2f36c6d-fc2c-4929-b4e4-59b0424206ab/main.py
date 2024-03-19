from surmount.base_class import Strategy, TargetAllocation

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker symbol for the tech company we're interested in
        self.ticker = "AAPL"

    @property
    def assets(self):
        # Indicate which assets this strategy will trade. In our case, just AAPL.
        return [self.ticker]

    @property
    def interval(self):
        # Define the interval for running this strategy. We'll run it daily.
        return "1day"

    def run(self, data):
        # Define the target allocation for AAPL. In this example, we allocate 100% of the portfolio to AAPL.
        # This means every day, the strategy will try to ensure all available funds are used to buy AAPL shares.
        allocation_dict = {self.ticker: 1.0}
        
        # Return the target allocation as a TargetAllocation object.
        return TargetAllocation(allocation_dict)