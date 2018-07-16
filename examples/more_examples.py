from bitfinex.rest.client import Client

client = Client('apiKey','apiSecret')

"""
    example on how to submit a rest request with multiple orders
    The following will make a list with 3 orders to buy 100 iota at 3 dollars, 100 iota at 4 dollars and 100 iota at 5 dollars
    The list is sent to the method place_multiple_orders
"""
orders=[]
for price in range(3, 6):
    print (price)
    payload = { "symbol": 'IOTUSD', "amount": '100', "price": str(price), "exchange": 'bitfinex', "side": 'buy', "type": 'limit' }
    orders.append(payload)

apiResponse = client.place_multiple_orders(orders)
print(apiResponse)



########## Bellow are examples for the methods using the REST API V2
"""
    example on how to use the  the wallets_balance method
"""
wb = client.wallets_balance()
for wallet in wb:
    print(wallet)



"""
    example on how to use the  the active_orders_rest2 method
"""
ao = client.active_orders_rest2("tIOTUSD")
for order in ao:
    print(order)



"""
    example on how to use the  the orders_history method
"""
oh = client.orders_history("tIOTUSD")
for order in oh:
    print(order)



"""
    example on how to use the  the order_trades method
"""
ot = client.order_trades("tIOTUSD",14365232219)
for trade in ot:
    print(trade)



"""
    example on how to use the  the trades_history method
"""
th = client.trades_history("tIOTUSD")
for trade in th:
    print(trade)