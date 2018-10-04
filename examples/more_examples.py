"""examples on how to use different methods from the rest library"""

from bitfinex import ClientV1 as Client1
from bitfinex import ClientV2 as Client2


if __name__ == "__main__":
    CLIENT = Client1('apiKey', 'apiSecret')

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

    # REST API V2 examples
    BTFXCLIENT = Client2('apiKey', 'apiSecret')

    # REST PUBLIC ENDPOINTS
    BTFXCLIENT.platform_status()             # Paltform Status
    BTFXCLIENT.tickers(['tIOTUSD', 'fIOT'])  # list of tickers
    BTFXCLIENT.ticker('tIOTUSD')             # ticker
    BTFXCLIENT.trades('fIOT')                # public trades for symbol
    BTFXCLIENT.trades('tIOTUSD')             # public trades for symbol
    BTFXCLIENT.books('tIOTUSD')              # books for tIOTUSD with price precision 0
    BTFXCLIENT.books('tIOTUSD', "P1")        # books for tIOTUSD with price precision 1

    PARAMS = {
        'key': 'funding.size',
        'size': '1m',
        'symbol': 'fUSD',
        'section': 'hist',
        'sort': '0'
    }
    BTFXCLIENT.stats(**PARAMS)              # statistics

    PARAMS = {
        'key': 'credits.size',
        'size': '1m',
        'symbol': 'fUSD',
        'section': 'hist',
        'sort': '0'
    }
    BTFXCLIENT.stats(**PARAMS)              # statistics

    PARAMS = {
        'key': 'pos.size',
        'size': '1m',
        'symbol': 'tIOTUSD',
        'side': 'short',
        'section': 'hist',
        'sort': '0'
    }
    BTFXCLIENT.stats(**PARAMS)              # statistics

    PARAMS = {
        'key': 'credits.size.sym',
        'size': '1m',
        'symbol': 'fUSD',
        'symbol2': 'tBTCUSD',
        'section': 'hist',
        'sort': '0'
    }
    BTFXCLIENT.stats(**PARAMS)              # statistics

    BTFXCLIENT.candles("1m", "tBTCUSD", "hist")             # 1 minute candles
    BTFXCLIENT.candles("1m", "tBTCUSD", "hist", limit='1')  # 1 minute candles , limit to 1 candle

    # REST CALCULATION ENDPOINTS
    BTFXCLIENT.market_average_price(symbol="tBTCUSD", amount="100", period="1m")
    BTFXCLIENT.foreign_exchange_rate(ccy1="IOT", ccy2="USD")

    # REST AUTHENTICATED ENDPOINTS
    WB = BTFXCLIENT.wallets_balance()
    for wallet in WB:
        print(wallet)

    AO = BTFXCLIENT.active_orders("tIOTUSD")
    for order in AO:
        print(order)

    OH = BTFXCLIENT.orders_history("tIOTUSD")
    for order in OH:
        print(order)

    OT = BTFXCLIENT.order_trades("tIOTUSD", 14395751815)
    for trade in OT:
        print(trade)

    TRADES = BTFXCLIENT.trades_history('tIOTUSD', limit=10)
    TH = BTFXCLIENT.trades_history("tIOTUSD")
    for trade in TH:
        print(trade)

    BTFXCLIENT.active_positions()

    BTFXCLIENT.funding_offers()
    BTFXCLIENT.funding_offers("fIOT")
    BTFXCLIENT.funding_offers_history('fOMG')
    BTFXCLIENT.funding_loans('fOMG')
    BTFXCLIENT.funding_loans_history('fOMG')
    BTFXCLIENT.funding_credits('fUSD')
    BTFXCLIENT.funding_credits_history('fUSD')
    BTFXCLIENT.funding_trades('fUSD')

    BTFXCLIENT.margin_info()
    BTFXCLIENT.margin_info('base')
    BTFXCLIENT.margin_info('tIOTUSD')

    BTFXCLIENT.funding_info('fIOT')

    BTFXCLIENT.movements()

    BTFXCLIENT.performance()

    BTFXCLIENT.alert_list()
    BTFXCLIENT.alert_set('price', 'tIOTUSD', 3)
    BTFXCLIENT.alert_delete('tIOTUSD', 1)

    BTFXCLIENT.calc_available_balance('tIOTUSD', 1, 0.02, 'EXCHANGE')

    BTFXCLIENT.ledgers('IOT')
