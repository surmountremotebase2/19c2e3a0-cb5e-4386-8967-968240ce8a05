from surmount.base_class import Strategy, TargetAllocation
from surmount.logging import log
from surmount.data import Asset, InstitutionalOwnership, InsiderTrading
import pandas_ta as ta
import pandas as pd

def SMAVol(ticker, data, length):
    close = [i[ticker]["volume"] for i in data]
    d = ta.sma(pd.Series(close), length=length)
    if d is None:
        return None
    return d.tolist()

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
        return "1day"

    def run(self, data):
        allocation_dict = {}
        ohlcv_data = data["ohlcv"]

        for ticker in self.tickers:
            # Check if we have enough data points (at least 4 days to make a decision)
            if len(data["ohlcv"]) < 40:
                allocation_dict[ticker] = 0
                continue

            vols = [i[ticker]["volume"] for i in data["ohlcv"]]
            smavol40 = SMAVol(ticker, data["ohlcv"], 40)
            smavol5 = SMAVol(ticker, data["ohlcv"], 5)

            if len(vols)==0:
                    self.allocation_dict[ticker] = 0
                    
            if smavol5[-1]/smavol40[-1]-1>0:
                    self.allocation_dict[ticker] = 1
            else: self.allocation_dict[ticker] = 0
       
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