from tornado.web import RequestHandler, HTTPError
from utils import *
from websocket import create_connection

import json
import requests
import websocket
import os


class MainRequestHandler(RequestHandler):
    def get(self):
        self.write("PoC for REST API...")

class order(RequestHandler):
    # input json body {orderIDs: [], tickers: [], dates: []}
    # filters for tickers and dates still have to be implemented
    async def get(self):
        parsed_data = json.loads(self.request.body)

        for i in parsed_data['orderIDs']:
            if i[0:2] == "01":
                cursor = self.settings['db'].buy_side_market.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
            if i[0:2] == "02":
                cursor = self.settings['db'].sell_side_limit.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
            if i[0:2] == "03":
                cursor = self.settings['db'].trailing_stop.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
            if i[0:2] == "04":
                cursor = self.settings['db'].bracket_order.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
    async def post(self):
        parsed_data = json.loads(self.request.body)

        if parsed_data['order_type'] == "buy_side_market":
            order_id = await id_gen("buy_side_market")
            parsed_data['orderID'] = order_id
            
            await self.settings['db'].buy_side_market.insert_one(parsed_data)
            self.write("200 - successful")
        
        if parsed_data['order_type'] == "sell_side_limit":
            order_id = await id_gen("sell_side_limit")
            parsed_data['orderID'] = order_id

            await self.settings['db'].buy_side_market.insert_one(parsed_data)
            self.write("200 - successful")
        
        if parsed_data['order_type'] == "trailing_stop":
            order_id = await id_gen("trailing_stop")
            parsed_data['orderID'] = order_id

            await self.settings['db'].buy_side_market.insert_one(parsed_data)
            self.write("200 - successful")
        
        if parsed_data['order_type'] == "bracket_order":
            order_id = await id_gen("bracket_order")
            parsed_data['orderID'] = order_id

            await self.settings['db'].buy_side_market.insert_one(parsed_data)
            self.write("200 - successful")

         


# WORK IN PROGRESS
# input json body {ticker: "", quote: "y or n", bars: "y or n", trades: "y or n"}
class realMarketData(RequestHandler):
    def get(self):
        parsed_json = json.loads(self.request.body)

        ws = create_connection('wss://stream.data.alpaca.markets/v2/iex')
        
        ws.send(json.dumps({"action": "auth", "key": os.environ["ALPACA_KEY"], "secret": os.environ["ALPACA_SECRET"]}))
        result = ws.recv()
        print(result)

        result = ws.recv()
        print(result)

        print("---------------------------" + "\n")

        if parsed_json['quote'] == "y" and parsed_json['bars'] == "n" and parsed_json['trades'] == "n":
            ws.send(json.dumps({"action":"subscribe", "quotes":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)

        if parsed_json['quote'] == "n" and parsed_json['bars'] == "y" and parsed_json['trades'] == "n":
            ws.send(json.dumps({"action":"subscribe", "bars":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)
        
        if parsed_json['quote'] == "n" and parsed_json['bars'] == "n" and parsed_json['trades'] == "y":
            ws.send(json.dumps({"action":"subscribe", "trades":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)
        
        if parsed_json['quote'] == "y" and parsed_json['bars'] == "y" and parsed_json['trades'] == "n":
            ws.send(json.dumps({"action":"subscribe",  "quotes":[parsed_json['ticker']], "bars":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)
        
        if parsed_json['quote'] == "n" and parsed_json['bars'] == "y" and parsed_json['trades'] == "y":
            ws.send(json.dumps({"action":"subscribe", "bars":[parsed_json['ticker']], "trades":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)
        
        if parsed_json['quote'] == "y" and parsed_json['bars'] == "n" and parsed_json['trades'] == "y":
            ws.send(json.dumps({"action":"subscribe", "quotes":[parsed_json['ticker']], "trades":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)
        
        if parsed_json['quote'] == "y" and parsed_json['bars'] == "y" and parsed_json['trades'] == "y":
            ws.send(json.dumps({"action":"subscribe", "quotes":[parsed_json['ticker']], "bar": [parsed_json['ticker']], "trades":[parsed_json['ticker']]}))
            result = ws.recv()
            print("\n" + result)


# WORK IN PROGRESS
class historicMarketData(RequestHandler):
    pass

