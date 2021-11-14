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

        for i in parsed_data['orderIDs']:
            if i[0:2] == "01":
                cursor = self.settings['db'].buy_side_market.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
                self.set_status(200, "order fetched")
            elif i[0:2] == "02":
                cursor = self.settings['db'].sell_side_limit.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
                self.set_status(200, "order fetched")
            elif i[0:2] == "03":
                cursor = self.settings['db'].trailing_stop.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
                self.set_status(200, "order fetched")
            elif i[0:2] == "04":
                cursor = self.settings['db'].bracket_order.find({"orderID": i})      
                if cursor is None:
                    raise HTTPError(
                        404, f"orders do not exist"
                    )
                for document in await cursor.to_list(length=100):
                    self.write(str(document))
                self.set_status(200, "order fetched")

    async def post(self):
        parsed_data = json.loads(self.request.body)

        if parsed_data['order_type'] == "buy_side_market":
            order_id = await id_gen("buy_side_market")
            parsed_data['orderID'] = order_id

            api.submit_order(
                symbol=parsed_data['ticker'],
                qty=parsed_data['quantity'],
                side='buy',
                type='market',
                time_in_force='gtc',
                client_order_id=order_id
            )
            print("[+] order submitted thru alpaca")
            
            await self.settings['db'].buy_side_market.insert_one(parsed_data)
            print("[+] order logged in db")

            self.set_status(200, "order submitted and logged")
        
        elif parsed_data['order_type'] == "sell_side_limit":
            order_id = await id_gen("sell_side_limit")
            parsed_data['orderID'] = order_id

            api.submit_order(
                symbol=parsed_data['ticker'],
                qty=parsed_data['quantity'],
                side='sell',
                type='limit',
                time_in_force='opg',
                limit_price=parsed_data['lim_price'],
                client_order_id=order_id
            )
            print("[+] order submitted thru alpaca")

            await self.settings['db'].sell_side_limit.insert_one(parsed_data)
            print("[+] order logged in db")
            
            self.set_status(200, "order submitted and logged")
        
        elif parsed_data['order_type'] == "trailing_stop":
            buy_order_id = await id_gen("buy_side_market")
            parsed_data['buy_orderID'] = buy_order_id

            trail_order_id = await id_gen("trailing_stop")
            parsed_data['trail_orderID'] = trail_order_id

            api.submit_order(
                symbol=parsed_data['ticker'],
                qty=parsed_data['quantity'],
                side='buy',
                type='market',
                time_in_force='gtc',
                client_order_id=buy_order_id
            )
            print("[+] buy side order submitted")

            if parsed_data['trail_price_or_percent'] == "price":
                api.submit_order(
                    symbol=parsed_data['ticker'],
                    qty=parsed_data['quantity'],
                    side='sell',
                    type='trailing_stop',
                    trail_price=parsed_data['trail_price'],
                    time_in_force='gtc',
                    client_order_id=trail_order_id
                )
                print("[+] trailing stop order submitted")

                await self.settings['db'].trailing_stop.insert_one(parsed_data)
                self.set_status(200, "order submitted and logged")
            
            elif parsed_data['trail_price_or_percent'] == "percent":
                api.submit_order(
                    symbol=parsed_data['ticker'],
                    qty=parsed_data['quantity'],
                    side='sell',
                    type='trailing_stop',
                    trail_price=parsed_data['trail_percent'],
                    time_in_force='gtc',
                    client_order_id=trail_order_id
                )
                print("[+] trailing stop order submitted")

                await self.settings['db'].trailing_stop.insert_one(parsed_data)
                self.set_status(200, "order submitted and logged")

        
        elif parsed_data['order_type'] == "bracket_order":
            order_id = await id_gen("bracket_order")
            parsed_data['orderID'] = order_id

            symbol_bars = api.get_barset(parsed_data['ticker'], 'minute', 1).df.iloc[0]
            symbol_price = symbol_bars[parsed_data['ticker']]['close']

            if parsed_data['strategy'] == "both":
                # buy a position and add a stop-loss and a take-profit of user specified percent
                api.submit_order(
                    symbol=parsed_data['ticker'],
                    qty=parsed_data['quantity'],
                    side='buy',
                    type='market',
                    time_in_force='gtc',
                    order_class='bracket',
                    stop_loss={'stop_price': symbol_price * (1.0 - (float(parsed_data['percentage']) / 100.0)),
                               'limit_price':  symbol_price * (1.0 - (float(parsed_data['percentage']) / 100.0) - 0.01)},
                    take_profit={'limit_price': symbol_price * (1.0 + (float(parsed_data['percentage']) / 100.0))},
                    client_order_id=order_id
                )
                print("[+] bracket order (both) submitted")

                await self.settings['db'].bracket_order.insert_one(parsed_data)
                self.set_status(200, "order submitted and logged")
            
            elif parsed_data['strategy'] == "stop-loss":
                api.submit_order(
                    symbol=parsed_data['ticker'],
                    qty=parsed_data['quantity'],
                    side='buy',
                    type='market',
                    time_in_force='gtc',
                    order_class='oto',
                    stop_loss={'stop_price': symbol_price * (1.0 - (float(parsed_data['percentage']) / 100.0))},
                    client_order_id=order_id
                )
                print("[+] bracket order (stop-loss) submitted")

                await self.settings['db'].bracket_order.insert_one(parsed_data)
                self.set_status(200, "order submitted and logged")


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


