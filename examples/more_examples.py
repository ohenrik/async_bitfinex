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



    ########## REST API V2 examples
    BTFXCLIENT = Client2('apiKey', 'apiSecret')

    ##### REST PUBLIC ENDPOINTS
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






    ##### REST CALCULATION ENDPOINTS
    BTFXCLIENT.market_average_price(symbol="tBTCUSD", amount="100", period="1m") # method 1
    BTFXCLIENT.foreign_exchange_rate(ccy1="IOT", ccy2="USD")                     # method 2




    ##### REST AUTHENTICATED ENDPOINTS
    WB = BTFXCLIENT.wallets_balance()                                 #method 1
    for wallet in WB:
        print(wallet)

    AO = BTFXCLIENT.active_orders("tIOTUSD")                          #method 2
    for order in AO:
        print(order)

    OH = BTFXCLIENT.orders_history("tIOTUSD")                         #method 3
    for order in OH:
        print(order)

    OT = BTFXCLIENT.order_trades("tIOTUSD", 14395751815)              #method 4
    for trade in OT:
        print(trade)

    TRADES = BTFXCLIENT.trades_history('tIOTUSD', limit=10)           #method 5
    TH = BTFXCLIENT.trades_history("tIOTUSD")
    for trade in TH:
        print(trade)

    BTFXCLIENT.active_positions()                                     #method 6

    BTFXCLIENT.funding_offers()                                       #method 7
    BTFXCLIENT.funding_offers("fIOT")                                 #method 7

    BTFXCLIENT.funding_offers_history('fOMG')                         #method 8

    BTFXCLIENT.funding_loans('fOMG')                                  #methon 9

    BTFXCLIENT.funding_loans_history('fOMG')                          #method 10

    BTFXCLIENT.funding_credits('fUSD')                                #method 11

    BTFXCLIENT.funding_credits_history('fUSD')                        #method 12

    BTFXCLIENT.funding_trades('fUSD')                                 #method 13

    BTFXCLIENT.margin_info()                                          #method 14
    BTFXCLIENT.margin_info('base')                                    #method 14
    BTFXCLIENT.margin_info('tIOTUSD')                                 #method 14

    BTFXCLIENT.funding_info('fIOT')                                   #method 15

    BTFXCLIENT.movements()                                            #method 16

    BTFXCLIENT.performance()                                          #method 17

    BTFXCLIENT.alert_list()                                           #method 18

    BTFXCLIENT.alert_set('price', 'tIOTUSD', 3)                       #method 19

    BTFXCLIENT.alert_delete('tIOTUSD', 1)                             #method 20

    BTFXCLIENT.calc_available_balance('tIOTUSD', 1, 0.02, 'EXCHANGE') #method 21

    BTFXCLIENT.ledgers('IOT')                                         #method 22
