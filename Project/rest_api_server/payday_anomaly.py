from strategy import *
from schedule import repeat, every, run_pending
from colorama import Fore

import datetime 
import time
import alpaca_trade_api as tradeapi
import json

# investment universe consists of the S&P500 index. Simply, buy and hold the index during the 16th day in the month during each month of the year.
# Buy 5% of portfolio value for SPY, do take profit at +10% and sell at -5% after purchase
# execute bracket order 1 minute before market closes
# reference: https://quantpedia.com/strategies/payday-anomaly/

creds = json.load(open('api.json',))

api = tradeapi.REST(
    creds["alpaca_apiKeyID"],
    creds["alpaca_secretKey"],
    creds["alpaca_endpoint"], api_version='v2'
)
account = api.get_account()
port_amt = float(account.equity) * 0.05

# get daily open price of SPY
barset = api.get_barset('SPY', 'day', limit=1)
spy_bar = barset['SPY']
day_open = spy_bar[0].o

quant = int(port_amt / day_open)

paydayAnom = strategy()
exc_order = bracket_order("SPY", quant, "both", 5, 10)

def checkDay():
    d = datetime.datetime.now()
    print(d)
    return d.strftime("%d")

@repeat(every(1).days)
def runStrat():
    print(Fore.YELLOW + "[!] running strategy..." + Fore.RESET)
    checkDay()
    if checkDay() == "16":
        if time.strftime("%I:%M") == "02:59":
            paydayAnom.addRule(exc_order)
        else:
            print(Fore.RED + "[-] not 1 min b4 market closes...")
    else:
        print(Fore.RED + "[-] not 16th day of month, no order executions...")


while True:
    print(Fore.GREEN + "[+] schedueler running..." + Fore.RESET)
    run_pending()
    time.sleep(1)


