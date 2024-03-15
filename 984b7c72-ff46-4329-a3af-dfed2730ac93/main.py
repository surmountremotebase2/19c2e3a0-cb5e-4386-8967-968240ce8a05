import numpy as np
import pandas as pd
from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA
from surmount.data import Asset

class TradingStrategy(Strategy):
    def __init__(self):
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
        # Initialize a dictionary to track the holding status of each stock 
        self.stock_holdings = {ticker: False for ticker in self.tickers}

    @property
    def interval(self):
        # Using daily interval for checking the price gain over 3 days
        return "1day"

    @property
    def assets(self):
        return self.tickers

    def run(self, data):
        allocation_dict = {}

        ohlcv_data = data["ohlcv"]
        
        for ticker in self.tickers:
            # Check if we have enough data points (at least 4 days to make a decision)
            if len(data["ohlcv"]) < 10:
                allocation_dict[ticker] = 0
                continue

            # Create short and long moving averages
            short_signal = SMA(ticker, ohlcv_data, 10)
            long_signal = SMA(ticker, ohlcv_data, 50)

            # Generate buy and sell signals
            signal = 1 if short_signal[-1] > long_signal[-1] else 0


            if signal and self.stock_holdings[ticker] == False:
                allocation_dict[ticker] = 1  # Allocate all to this stock
                self.stock_holdings[ticker] = True  # Update the holding status
            else:
                allocation_dict[ticker] = 0  # Allocate all to this stock
                self.stock_holdings[ticker] = False  # Update the holding status

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