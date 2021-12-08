from utils import *
from handlers import api
import motor

uri = os.environ["MONGO_URI"]
motor_client = motor.motor_tornado.MotorClient(uri)
db = motor_client.orders

class market_interface:
    async def get_order_by_id(order_id):
        if order_id[0:2] == "01":
            return await db.buy_side_market.find_one({"orderID": order_id})
        elif order_id[0:2] == "02":
            return await db.sell_side_limit.find_one({"orderID": order_id})
        elif order_id[0:2] == "03":
            return await db.trailing_stop.find_one({"trail_orderID": order_id})
        elif order_id[0:2] == "04":
            return await db.bracket_order.find_one({"orderID": order_id})

    async def buy_side_market(ticker, quantity):
        order_id = await id_gen("buy_side_market")
        api.submit_order(
            symbol = ticker,
            qty = quantity,
            side = "buy",
            type = "market",
            time_in_force = "gtc",
            client_order_id = order_id
        )
        await db.buy_side_market.insert_one({
            "order_type": "buy_side_market",
            "ticker": ticker,
            "quantity": quantity,
            "orderID": order_id
        })

    async def sell_side_limit(ticker, quantity, lim_price):
        order_id = await id_gen("sell_side_limit")
        api.submit_order(
            symbol = ticker,
            qty = quantity,
            side = "sell",
            type = "limit",
            time_in_force = "opg",
            limit_price = lim_price,
            client_order_id = order_id
        )
        await db.sell_side_limit.insert_one({
            "order_type": "sell_side_limit",
            "ticker": ticker,
            "quantity": quantity,
            "lim_price": lim_price,
            "orderID": order_id
        })

    async def trailing_stop(ticker, quantity, trail_price_or_percent, trail_price):
        buy_order_id = await id_gen("buy_side_market")
        trail_order_id = await id_gen("trailing_stop")
        api.submit_order(
            symbol = ticker,
            qty = quantity,
            side = "buy",
            type = "market",
            time_in_force = "gtc",
            client_order_id = buy_order_id
        )
        if trail_price_or_percent == "price":
            api.submit_order(
                symbol = ticker,
                qty = quantity,
                side = "sell",
                type = "trailing_stop",
                trail_price = trail_price,
                time_in_force = "gtc",
                client_order_id = trail_order_id
            )
        elif trail_price_or_percent == "percent":
            api.submit_order(
                symbol = ticker,
                qty = quantity,
                side = "sell",
                type = "trailing_stop",
                trail_price = trail_price,
                time_in_force = "gtc",
                client_order_id = trail_order_id
            )
        await db.trailing_stop.insert_one({
            "order_type": "trailing_stop",
            "ticker": ticker,
            "quantity": quantity,
            "trail_price_or_percent": trail_price_or_percent,
            "trail_price": trail_price,
            "buy_orderID": buy_order_id,
            "trail_orderID": trail_order_id
        })

    async def bracket_order(ticker, quantity, strategy, percentage):
        order_id = await id_gen("bracket_order")
        symbol_bars = api.get_barset(ticker, "minute", 1).df.iloc[0]
        symbol_price = symbol_bars[ticker]["close"]

        if strategy == "both":
            # buy a position and add a stop-loss and a take-profit of user specified percent
            api.submit_order(
                symbol = ticker,
                qty = quantity,
                side = "buy",
                type = "market",
                time_in_force = "gtc",
                order_class = "bracket",
                stop_loss = {"stop_price": symbol_price * (1.0 - (float(percentage) / 100.0)),
                           "limit_price":  symbol_price * (1.0 - (float(percentage) / 100.0) - 0.01)},
                take_profit = {"limit_price": symbol_price * (1.0 + (float(percentage) / 100.0))},
                client_order_id = order_id
            )
        elif strategy == "stop-loss":
            api.submit_order(
                symbol = ticker,
                qty = quantity,
                side = "buy",
                type = "market",
                time_in_force = "gtc",
                order_class = "oto",
                stop_loss = {"stop_price": symbol_price * (1.0 - (float(percentage) / 100.0))},
                client_order_id = order_id
            )
        await db.bracket_order.insert_one({
            "order_type": "bracket_order",
            "ticker": ticker,
            "quantity": quantity,
            "strategy": strategy,
            "percentage": percentage,
            "orderID": order_id
        })
