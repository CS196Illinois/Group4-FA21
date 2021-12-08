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
        self.rule_chain = []
    
    def __len__(self):
        return len(self.rule_chain)

    def addRule(self, order):
        self.rule_chain.append(order)
        order.execute()
         


class order():
    def __init__(self, sym, qty):
        self.symbol = sym
        self.quantity = qty 

    def execute(self):
        pass


class buy_order(order):
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
        super().__init__(sym, qty)
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
    def __init__(self, sym, qty, strat, stop_perc, take_perc=None):
        super().__init__(sym, qty)
        self.strategy = strat
        self.stop_percentage = stop_perc

        if self.strategy == "both":
            self.take_percentage = take_perc


    def execute(self):
        symbol_bars = api.get_barset(self.symbol, "minute", 1).df.iloc[0]
        symbol_price = symbol_bars[self.symbol]["close"]

        if self.strategy == "both":
            # buy a position and add a stop-loss and a take-profit of user specified percent
            api.submit_order(
                symbol=self.symbol,
                qty=self.quantity,
                side='buy',
                type='market',
                time_in_force='gtc',
                order_class='bracket',
                stop_loss={'stop_price': symbol_price * (1.0 - (self.stop_percentage / 100.0)),
                           'limit_price':  symbol_price * (1.0 - (self.stop_percentage / 100.0) - 0.01)},
                take_profit={'limit_price': symbol_price * (1.0 + (self.take_percentage / 100.0))}
            )
            print(Fore.GREEN + "[+] new bracket order (stop-loss + take-profit) submitted" + Fore.RESET + '\n')
        
        elif self.strategy == "stop-loss":
            api.submit_order(
                symbol=self.symbol,
                qty=1,
                side='buy',
                type='market',
                time_in_force='gtc',
                order_class='oto',
                stop_loss={'stop_price': symbol_price * (1.0 - (self.percent / 100.0))},
            )
            print(Fore.GREEN + "[+] new bracket order (stop-loss) submitted" + Fore.RESET + '\n')



class trailing_stop_order(order):
    def __init__(self, sym, qty, pp, price, percent):
        super().__init__(sym, qty)
        self.percent_or_price = pp

        if self.percent_or_price == "price":
            # a dollar value away from the highest water mark. 
            # If you set this to 2.00 for a sell trailing stop, 
            # the stop price is always hwm - 2.00.
            self.trail_price = price 
        elif self.percent_or_price == "percent":
            # a percent value away from the highest water mark. 
            # If you set this to 1.0 for a sell trailing stop, 
            # the stop price is always hwm * 0.99.
            self.trail_percent = percent


    def execute(self):
        if self.percent_or_price == "price":
            api.submit_order(
                symbol=self.symbol,
                qty=self.quantity,
                side='sell',
                type='trailing_stop',
                trail_price=self.trail_price,
                time_in_force='gtc'
            )
            print(Fore.GREEN + "[+] new trailing stop order (trail price) submitted" + Fore.RESET + '\n')

        
        elif self.percent_or_price == "price":
            api.submit_order(
                symbol=self.symbol,
                qty=self.quantity,
                side='sell',
                type='trailing_stop',
                trail_price=self.trail_price,
                time_in_force='gtc'
            )
            print(Fore.GREEN + "[+] new trailing stop order (trail percent) submitted" + Fore.RESET + '\n')
