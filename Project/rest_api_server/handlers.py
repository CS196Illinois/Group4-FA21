from tornado.web import RequestHandler, HTTPError
from tornado.websocket import WebSocketHandler
from utils import *

import alpaca_trade_api as alpaca
import json
import requests
import websocket

creds = json.load(open('api.json',))

api = alpaca.REST(
    creds["alpaca_apiKeyID"],
    creds["alpaca_secretKey"],
    creds["alpaca_endpoint"], api_version='v2'
)

class MainRequestHandler(RequestHandler):
    def get(self):
        self.write("PoC for shepherd's REST API...")

class order(RequestHandler):
    async def get(self):
        parsed_data = json.loads(self.request.body)
        if not isinstance(parsed_data['orderIDs'], list):
            self.set_status(400, "to get orders, you must provide a list named orderIDs")
            return
        for order_id in parsed_data['orderIDs']:
            order = await market_interface.get_order_by_id(order_id)
            if not order is None:
                self.write(str(order))
        self.set_status(200, "successfully fetched all orders")

    async def post(self):
        parsed_data = json.loads(self.request.body)

        if parsed_data['order_type'] == "buy_side_market":
            await market_interface.buy_side_market(parsed_data['ticker'], parsed_data['quantity'])
            self.set_status(200, "order submitted and logged")

        elif parsed_data['order_type'] == "sell_side_limit":
            await market_interface.sell_side_limit(parsed_data['ticker'], parsed_data['quantity'], parsed_data['lim_price'])
            self.set_status(200, "order submitted and logged")

        elif parsed_data['order_type'] == "trailing_stop":
            if parsed_data['trail_price_or_percent'] == "price":
                await market_interface.trailing_stop(parsed_data['ticker'], parsed_data['quantity'], parsed_data['trail_price_or_percent'], parsed_data['trail_price'])
                self.set_status(200, "order submitted and logged")
            elif parsed_data['trail_price_or_percent'] == "percent":
                await market_interface.trailing_stop(parsed_data['ticker'], parsed_data['quantity'], parsed_data['trail_price_or_percent'], parsed_data['trail_percent'])
                self.set_status(200, "order submitted and logged")

        elif parsed_data['order_type'] == "bracket_order":
            await market_interface.bracket_order(parsed_data['ticker'], parsed_data['quantity'], parsed_data['strategy'], parsed_data['percentage'])
            self.set_status(200, "order submitted and logged")


class portfolioInfo(RequestHandler):
    async def post(self):
        account = api.get_account()

        # Check our current balance vs. our balance at the last market close
        balance_change = float(account.equity) - float(account.last_equity)
        info = {"account_id": account.id, "account_number": account.account_number, "cash": account.cash, "equity": account.equity, "gain_loss": balance_change}

        await self.settings['portfolio_db'].portfolio_info.insert_one(info)
        self.set_status(200, "portfolio gain/loss logged")


# [!] might need some changes depending on how i figure out client side
class realMarketData(WebSocketHandler):
    def open(self):
        parsed_json = json.loads(self.request.body)
        socket = "wss://stream.data.alpaca.markets/v2/iex"

        # authenticate alpaca api
        ws = websocket.WebSocketApp(socket, on_open=self.open(), on_message=self.on_message(), on_close=self.on_close())
        auth = {"action": "auth", "key": creds["alpaca_apiKeyID"], "secret": creds["alpaca_secretKey"]}
        ws.send(json.dump(auth))

        if parsed_json['quotes'] == "y" and parsed_json['bars'] == "n" and parsed_json['trades'] == "n":
            subscription = {"action":"subscribe", "quotes":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))

        elif parsed_json['quotes'] == "n" and parsed_json['bars'] == "y" and parsed_json['trades'] == "n":
            subscription = {"action":"subscribe", "bars":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))

        elif parsed_json['quotes'] == "n" and parsed_json['bars'] == "n" and parsed_json['trades'] == "y":
            subscription = {"action":"subscribe", "bars":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))

        elif parsed_json['quotes'] == "y" and parsed_json['bars'] == "y" and parsed_json['trades'] == "n":
             subscription = {"action":"subscribe",  "quotes":[parsed_json['ticker']], "bars":["*"]}
             ws.send(json.dumps(subscription))

        elif parsed_json['quotes'] == "n" and parsed_json['bars'] == "y" and parsed_json['trades'] == "y":
            subscription = {"action":"subscribe", "bars":[parsed_json['ticker']], "trades":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))

        elif parsed_json['quotes'] == "y" and parsed_json['bars'] == "n" and parsed_json['trades'] == "y":
            subscription = {"action":"subscribe", "quotes":[parsed_json['ticker']], "trades":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))


        elif parsed_json['quotes'] == "y" and parsed_json['bars'] == "y" and parsed_json['trades'] == "y":
            subscription = {"action":"subscribe", "quotes":[parsed_json['ticker']], "trades":[parsed_json['ticker']]}
            ws.send(json.dumps(subscription))

    def on_message(self, message):
        print("[!] received message")
        self.write_message(message)

    def on_close(self):
        print("web socket closed")



# [!] working on it rn
class historicMarketData(RequestHandler):
    def get(self):
         parsed_data = json.loads(self.request.body)
