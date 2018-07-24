"""examples on how to use different methods from the rest library"""

from bitfinex.rest.client import Client
from bitfinex.rest.restv2 import Client as Client2


if __name__ == "__main__":
    CLIENT = Client('apiKey', 'apiSecret')

    """
    example on how to submit a rest request with multiple orders
    The following will make a list with 3 orders to buy 100 iota at 3 dollars,
    100 iota at 4 dollars and 100 iota at 5 dollars
    The list is sent to the method place_multiple_orders
    """
    ORDERS = []
    for price in range(3, 6):
        print(price)
        payload = {
            "symbol": 'IOTUSD',
            "amount": '100',
            "price": str(price),
            "exchange": 'bitfinex',
            "side": 'buy',
            "type": 'limit'
        }
        ORDERS.append(payload)

    APIRESPONSE = CLIENT.place_multiple_orders(ORDERS)
    print(APIRESPONSE)



    ########## Bellow are examples for the methods using the REST API V2

    BTFXCLIENT = Client2('apiKey', 'apiSecret')


    BTFXCLIENT.platform_status()             #method 1 Paltform Status
    BTFXCLIENT.tickers(['tIOTUSD', 'fIOT'])  #method 2 list of tickers
    BTFXCLIENT.ticker('tIOTUSD')             #method 3 ticker
    BTFXCLIENT.trades('fIOT')                #method 4 public trades for symbol
    BTFXCLIENT.trades('tIOTUSD')             #method 4 public trades for symbol
    BTFXCLIENT.books('tIOTUSD')              #method 5 books for tIOTUSD with price precision 0
    BTFXCLIENT.books('tIOTUSD', "P1")        #method 5 books for tIOTUSD with price precision 1

    PARAMS = {
        'key'     : 'funding.size',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    BTFXCLIENT.stats(**PARAMS)              #method 6 statistics

    PARAMS = {
        'key'     : 'credits.size',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    BTFXCLIENT.stats(**PARAMS)              #method 6 statistics

    PARAMS = {
        'key'     : 'pos.size',
        'size'    : '1m',
        'symbol'  : 'tIOTUSD',
        'side'    : 'short',
        'section' : 'hist',
        'sort'    : '0'
    }
    BTFXCLIENT.stats(**PARAMS)              #method 6 statistics


    PARAMS = {
        'key'     : 'credits.size.sym',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'symbol2' : 'tBTCUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    BTFXCLIENT.stats(**PARAMS)              #method 6 statistics


    BTFXCLIENT.candles("1m", "tBTCUSD", "hist")            #method 7 candles
    BTFXCLIENT.candles("1m", "tBTCUSD", "hist", limit='1') #method 7 candles


    #example on how to use the  the wallets_balance method
    WB = BTFXCLIENT.wallets_balance()
    for wallet in WB:
        print(wallet)


    #example on how to use the  the active_orders_rest2 method
    AO = BTFXCLIENT.active_orders("tIOTUSD")
    for order in AO:
        print(order)


    #example on how to use the  the orders_history method
    OH = BTFXCLIENT.orders_history("tIOTUSD")
    for order in OH:
        print(order)


    #example on how to use the  the order_trades method
    OT = BTFXCLIENT.order_trades("tIOTUSD", 14365232219)
    for trade in OT:
        print(trade)


    #example on how to use the  the trades_history method
    TH = BTFXCLIENT.trades_history("tIOTUSD")
    for trade in TH:
        print(trade)




    BTFXCLIENT.foreign_exchange_rate(ccy1="IOT", ccy2="USD")
    BTFXCLIENT.market_average_price(symbol="tBTCUSD", amount="100", period="1m")







    BTFXCLIENT.user_settings_read('?')
    BTFXCLIENT.ledgers()
    BTFXCLIENT.calc_available_balance('tIOTUSD', 1, 1.13, 'EXCHANGE')
    BTFXCLIENT.alert_set('price', 'tIOTUSD', 1)
    BTFXCLIENT.alert_delete('tIOTUSD', 1)
    BTFXCLIENT.alert_list()
    BTFXCLIENT.performance()
    BTFXCLIENT.movements()
    BTFXCLIENT.margin_info()
    BTFXCLIENT.margin_info('base')
    BTFXCLIENT.margin_info('tIOTUSD')
    BTFXCLIENT.funding_info('fIOT')
    BTFXCLIENT.funding_trades()
    BTFXCLIENT.funding_credits()
    BTFXCLIENT.funding_credits_history()
    BTFXCLIENT.funding_loans()
    BTFXCLIENT.funding_loans_history()
    BTFXCLIENT.funding_offers()
    BTFXCLIENT.funding_offers_history()
    BTFXCLIENT.active_positions()
    BTFXCLIENT.wallets_balance()
    BTFXCLIENT.active_orders()
    BTFXCLIENT.orders_history('tIOTUSD')
    BTFXCLIENT.order_trades('tIOTUSD', 14395751815)
    BTFXCLIENT.trades_history('tIOTUSD')

    TRADES = BTFXCLIENT.trades_history('tIOTUSD', limit=10)

    for trade in TRADES:
        print(trade)
