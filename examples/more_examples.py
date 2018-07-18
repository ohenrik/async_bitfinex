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
from bitfinex.rest.restv2 import Client
btfx_client = Client('apiKey','apiSecret')
"""
    example on how to use the  the wallets_balance method
"""
wb = btfx_client.wallets_balance()
for wallet in wb:
    print(wallet)



"""
    example on how to use the  the active_orders_rest2 method
"""
ao = btfx_client.active_orders_rest2("tIOTUSD")
for order in ao:
    print(order)



"""
    example on how to use the  the orders_history method
"""
oh = btfx_client.orders_history("tIOTUSD")
for order in oh:
    print(order)



"""
    example on how to use the  the order_trades method
"""
ot = btfx_client.order_trades("tIOTUSD",14365232219)
for trade in ot:
    print(trade)



"""
    example on how to use the  the trades_history method
"""
th = btfx_client.trades_history("tIOTUSD")
for trade in th:
    print(trade)




btfx_client.foreign_exchange_rate(ccy1="IOT",ccy2="USD")

btfx_client.market_average_price(symbol="tBTCUSD",amount="100",period="1m")


btfx_client.candles("1m","tBTCUSD","hist")
btfx_client.candles("1m","tBTCUSD","hist",limit='1')


params = {
    'key'     : 'funding.size',
    'size'    : '1m',
    'symbol'  : 'fUSD',
    'section' : 'hist',
    'sort'    : '0'
}
btfx_client.stats(**params)

params = {
    'key'     : 'credits.size',
    'size'    : '1m',
    'symbol'  : 'fUSD',
    'section' : 'hist',
    'sort'    : '0'
}
btfx_client.stats(**params)

params = {
    'key'     : 'pos.size',
    'size'    : '1m',
    'symbol'  : 'tIOTUSD',
    'side'    : 'short',
    'section' : 'hist',
    'sort'    : '0'
}
btfx_client.stats(**params)


params = {
    'key'     : 'credits.size.sym',
    'size'    : '1m',
    'symbol'  : 'fUSD',
    'symbol2'  : 'tBTCUSD',
    'section' : 'hist',
    'sort'    : '0'
}
btfx_client.stats(**params)

btfx_client.stats("funding.size","1m","tBTCUSD","long","hist","1")
btfx_client.books('tIOTUSD')
btfx_client.ticker('tIOTUSD')
btfx_client.tickers(['tIOTUSD','fIOT'])
btfx_client.platform_status()
btfx_client.user_settings_read('?')
btfx_client.ledgers()
btfx_client.calc_available_balance("tIOTUSD",1,1.13,"EXCHANGE")
btfx_client.alert_set("price","tIOTUSD",1)
btfx_client.alert_delete("tIOTUSD",1)
btfx_client.alert_list()
btfx_client.performance()
btfx_client.movements()
btfx_client.margin_info()
btfx_client.funding_info()
btfx_client.funding_trades()
btfx_client.funding_credits()
btfx_client.funding_credits_history()
btfx_client.funding_loans()
btfx_client.funding_loans_history()
btfx_client.funding_offers()
btfx_client.funding_offers_history()
btfx_client.active_positions()
btfx_client.wallets_balance()
btfx_client.active_orders()
btfx_client.orders_history("tIOTUSD")
btfx_client.order_trades('tIOTUSD',14395751815)
btfx_client.trades_history("tIOTUSD")

trades = btfx_client.trades_history("tIOTUSD",limit=10)

for trade in trades:
    print(trade)
