from surmount.base_class import Strategy, TargetAllocation
from surmount.technical_indicators import SMA, BB
from surmount.logging import log

class TradingStrategy(Strategy):

    @property
    def assets(self):
        return ["TSLA", "TSLS"]

    @property
    def interval(self):
        return "1hour"

    def run(self, data):
        holdings = data["holdings"]
        data = data["ohlcv"]

        BP_stake = 0
        F_stake = 0

        F_bbands = BB("TSLA", data, 20, 1.4)
        F_ma = SMA("TSLA", data, 5)

        if len(data)<20:
            return TargetAllocation({})

        current_price = data[-1]["TSLA"]['close']

        if F_bbands is not None and current_price < F_bbands['lower'][-1] and F_ma[-1]>F_ma[-2]:
            log("going long")
            if holdings["TSLA"] >= 0:
                F_stake = min(1, holdings["TSLA"]+0.1)
            else:
                F_stake = 0.4
        elif F_bbands is not None and current_price > F_bbands['upper'][-1]:
            log("going short")
            if holdings["TSLS"] >= 0:
                BP_stake = min(1, holdings["TSLS"]+0.075)
            else:
                BP_stake = 0.2
        else:
            log("meh")
            F_stake = 0
            BP_stake = 0

        return TargetAllocation({"TSLS": BP_stake, "TSLA": F_stake})