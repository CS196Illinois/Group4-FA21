import requests
import websocket
import json


# /order POST request, market-side buy order
post_url = 'http://localhost:1337/api/v1/order'
req = """{"order_type": "buy_side_market", "ticker": "SPY", "quantity": "1000"}"""

send = requests.post(post_url, data=req)


# /order POST request, sell-side limit order
post_url = 'http://localhost:1337/api/v1/order'
req = """{"order_type": "sell_side_limit", "ticker": "TSLA", "quantity": "500", "lim_price": "1000.00"}"""

send = requests.post(post_url, data=req)


# /order POST request, trailing stop order
post_url = 'http://localhost:1337/api/v1/order'
req = """{"order_type": "trailing_stop", "ticker": "AAPL", "quantity": "100", "trail_price_or_percent": "price", "trail_price": "1.00"}"""

send = requests.post(post_url, data=req)


# /order POST request, bracket order
post_url = 'http://localhost:1337/api/v1/order'
req = """{"order_type": "bracket_order", "ticker": "MSFT", "quantity": "200", "strategy": "both", "percentage": "0.95"}"""

send = requests.post(post_url, data=req)


# /order GET request
get_url = 'http://localhost:1337/api/v1/order'
req = """{"orderIDs": ["011L5gO4", "0149y3gz"]}"""

get = requests.get(get_url, data=req)
print(get.text)


# /portfolioInfo POST
post_url = 'http://localhost:1337/api/v1/portfolioInfo'
post = requests.post(post_url)
print(post.text)


# [!] still work in progress
# /marketData real-time 

ws = websocket.create_connection('ws://localhost:1337/api/v1/marketData/realtime')
payload = """{ticker: "MSFT", quotes: "y", bars: "n", trades: "n"}"""

result = ws.recv()
print(result)
result = ws.recv()
print(result)

ws.send(payload)
result = ws.recv()
print(result)



# [!] to be done
# /marketData historic

