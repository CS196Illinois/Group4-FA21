import random 
import string
import motor
import os

'''
ID system:

buy_side_market - 01 prefix + random alphanumeric string of length 6
sell_side_limit - 02 prefix + random alphanumeric string of length 6
trailing_stop   - 03 prefix + random alphanumeric string of length 6
bracket_order   - 04 prefix + random alphanumeric string of length 6

'''

uri = os.environ["MONGO_URI"]
motor_client = motor.motor_tornado.MotorClient(uri)
db = motor_client.orders

def id_string_gen():
    temp_id = ''.join((random.choice(string.ascii_letters) for i in range(3)))
    temp_id += ''.join((random.choice(string.digits) for i in range(3)))

    temp_id_list = list(temp_id)
    random.shuffle(temp_id_list)
    final_id = ''.join(temp_id_list)

    return final_id

async def id_gen(order_type):
    if order_type == "buy_side_market":
        final_id = "01" + id_string_gen()
        if await db.buy_side_market.find_one({"orderID": final_id}) == None:
            return final_id

    if order_type == "sell_side_limit":
        final_id = "02" + id_string_gen()
        if await db.sell_side_limit.find_one({"orderID": final_id}) == None:
            return final_id
    
    if order_type == "trailing_stop":
        final_id = "03" + id_string_gen()
        if await db.trailing_stop.find_one({"orderID": final_id}) == None:
            return final_id
    
    if order_type == "bracket_order":
        final_id = "04" + id_string_gen()
        if await db.bracket_order.find_one({"orderID": final_id}) == None:
            return final_id


