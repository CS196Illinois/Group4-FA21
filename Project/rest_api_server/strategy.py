from colorama import Fore

import alpaca_trade_api as tradeapi
import json

creds = json.load(open('api.json',))

api = tradeapi.REST(
    creds["alpaca_apiKeyID"],
    creds["alpaca_secretKey"],
    creds["alpaca_endpoint"], api_version='v2'
)


class strategy():
    def __init__(self):
        self.order_freq = 0
        self.rule_chain = []

    def addRule(order):
        pass
         


class order():
    def __init__(self):
        pass 

    def execute(self):
        pass


class buy_order(order):
    def __init__(self, sym, qty):
        self.symbol = sym 
        self.quantity = qty

    def execute(self):
        api.submit_order(
            symbol=self.symbol,
            qty=self.quantity,
            side='buy',
            type='market',
            time_in_force='gtc'
        )
        print(Fore.GREEN + "[+] new buy-side market order submitted" + Fore.RESET + '\n')


class limit_sell_order(order):
    def __init__(self, sym, qty, lp):
        self.symbol = sym
        self.quantity = qty 
        self.lim_price = lp 

    def execute(self):
        api.submit_order(
            symbol=self.symbol,
            qty=self.quantity,
            side='sell',
            type='limit',
            time_in_force='opg',
            limit_price=self.lim_price,
        )
        print(Fore.GREEN + "[+] new sell-side limit order submitted" + Fore.RESET + '\n')


class bracket_order(order):
    def __init__(self, sym, qty, strat, perc=None):
        self.symbol = sym
        self.quantity = qty 
        self.strategy = strat

        if self.strategy == "both":
            #percentage for stop-loss and take-profit
            self.percentage = perc

    def execute(self):
        pass


class trailing_stop_order(order):
    def __init__(self):
        super().__init__()

    def execute(self):
        return super().execute()
