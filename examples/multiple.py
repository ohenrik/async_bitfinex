from bitfinex.client import Client

client = Client('apiKey','apiSecret')


orders=[]

for price in range(3, 6):
    print (price)
    payload = { "symbol": 'IOTUSD', "amount": '100', "price": str(price), "exchange": 'bitfinex', "side": 'buy', "type": 'limit' }
    orders.append(payload)


apiResponse = client.place_multiple_orders(orders)

print(apiResponse)
