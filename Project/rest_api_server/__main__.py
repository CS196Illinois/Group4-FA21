from tornado.web import Application, RequestHandler
from tornado.httpserver import HTTPServer
from tornado.ioloop import IOLoop
from tornado.platform.asyncio import AsyncIOMainLoop
from handlers import *

import motor
import os

def main():
    AsyncIOMainLoop().install()
    ioloop = IOLoop.current()

    application = Application([
        (r"/api/v1", MainRequestHandler),
        (r"/api/v1/order", order),
        (r"/api/v1/marketData/realtime", realMarketData),
        (r"/api/v1/marketData/historic", historicMarketData),
        (r"/api/v1/portfolioInfo", portfolioInfo)
    ],
    debug=True,
    autoreload=True)

    application.listen(1337)
    print(f'server is listening on port 1337')

    uri = os.environ["MONGO_URI"]
    motor_client = motor.motor_tornado.MotorClient(uri)
    application.settings['order_db'] = motor_client.orders
    application.settings['portfolio_db'] = motor_client.portfolio

    ioloop.start()

if __name__ == '__main__':
    main()
