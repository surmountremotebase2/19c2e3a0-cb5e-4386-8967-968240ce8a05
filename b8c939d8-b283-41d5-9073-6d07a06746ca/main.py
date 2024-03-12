from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership, InsiderTrading

class TradingStrategy(Strategy):
    def __init__(self):
        # Define the ticker of interest
        self.tickers = ["AAPL", "MSFT", "AMZN", "GOOGL", 
                        "META", "TSLA", "BRK.B", "JNJ", 
                        "JPM", "NVDA", "V", "PG", "HD", "MA", 
                        "INTC", "UNH", "BAC", "DIS", "ADBE", "CRM", 
                        "PYPL", "NFLX", "CMCSA", "KO", "T", "PEP", 
                        "MRK", "XOM", "WMT", "CSCO", "ABT", "VZ", "NKE", 
                        "ABBV", "TMO", "CVX", "ACN", "MCD", "COST", "TXN", 
                        "NEE", "WFC", "HON", "ORCL", "LLY", "DHR", "PM", "QCOM", 
                        "AMGN", "UNP", "IBM", "AMD", "AXP", "LIN", "CAT", 
                        "MDT", "GS", "LOW", "UPS", "SBUX", "RTX", "SPGI", "MMM", 
                        "BLK", "INTU", "DUK", "MO", "BDX", "ISRG", "CI", "CSX", 
                        "PLD", "VRTX", "TGT", "LMT", "ICE", "ADI", "SO", 
                        "BMY", "CME", "SYK", "SPG", "FIS", "REGN", "ZTS", "NOW", "CHTR",
                        "GILD", "ATVI", "MMC", "ADP", "CB", "SCHW", "BSX"]
        self.lookback_periods = 30  # Lookback period to calculate average volume
        self.large_sell_threshold = 10000  # Define what is considered a large sell order
        self.buy_signal_activated = False  # Track if a buy signal has been activated
        self.allocation_dict = {ticker: 0 for ticker in self.tickers}  # Initialize allocation dict for all tickers

    @property
    def assets(self):
        # Only interested in trading MSFT for this strategy
        return self.tickers

    @property
    def interval(self):
        # Strategy operates on 1-minute intervals
        return "1min"

    def run(self, data):
        for ticker in self.tickers:
            # Extract the recent volume and trading data for the ticker
            recent_data = data["ohlcv"][ticker]
        
            # Calculate the average volume over the lookback period
            average_volume = sum([i["volume"] for i in recent_data[-self.lookback_periods:]]) / self.lookback_periods
            current_volume = recent_data[-1]["volume"]
            transaction_type = recent_data[-1].get("acquisitionOrDisposition", "")
            transaction_amt = recent_data[-1].get("securitiesTransacted", 0)

            # If the current volume is significantly higher than the average, buy the ticker
            if current_volume > average_volume and not self.buy_signal_activated:
                log(f"Buy signal activated for {ticker} due to high volume")
                self.allocation_dict[ticker] = 1  # Buy (go long on) the ticker
                self.buy_signal_activated = True
            # Sell the ticker if a large sell order is detected
            elif self.buy_signal_activated and transaction_type == "D" and transaction_amt > self.large_sell_threshold:
                log(f"Sell signal activated for {ticker} due to large sell order")
                self.allocation_dict[ticker] = 0  # Sell the ticker
                self.buy_signal_activated = False
            # Continue holding the ticker if neither condition is met but a buy was previously activated
            elif self.buy_signal_activated:
                self.allocation_dict[ticker] = 1  # Maintain current holding

        # Filter out the stocks with value 1
        allocated_stocks = [ticker for ticker, value in allocation_dict.items() if value == 1]
        
        # Calculate total number of allocated stocks
        total_allocated = len(allocated_stocks)
        
        # If no stocks are allocated, return an empty list
        if total_allocated == 0:
            return TargetAllocation({})

        # Calculate percentage share for each allocated stock
        percentage_share = (1 / total_allocated) - 0.01
        
        # Update the dictionary with percentage share for allocated stocks
        for ticker in allocated_stocks:
            allocation_dict[ticker] = percentage_share
        
        # Return the target allocation
        return TargetAllocation(allocation_dict)