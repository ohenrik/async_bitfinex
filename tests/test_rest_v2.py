"""Tests for the v2 rest api"""
import json
import pytest
import requests_mock as rmock
from bitfinex.rest import ClientV2 as Client

# pylint: disable=W0621,C0111

@pytest.fixture
def client():
    return Client("key", "secret")


def test_platform_status(client, requests_mock):
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text='[1]'
    )
    platform_status = client.platform_status()
    assert platform_status == [1]


def test_tickers_url_is_ok(client, requests_mock):
    response_text = "[]"
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.tickers(['tIOTBTC', 'tIOTUSD'])
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/tickers?symbols=tIOTBTC,tIOTUSD'
    )

def test_tickers_response(client, requests_mock):
    response_text = json.dumps([
        ['tIOTBTC',
         0.00012012,
         207246.56609548,
         0.00012048,
         230371.29034138,
         -8.28e-06,
         -0.0644,
         0.00012035,
         3215468.26026294,
         0.00012863,
         0.00011545],
        ['tIOTUSD',
         0.95969,
         24306.55703175,
         0.96214,
         60186.47595187,
         -0.03534,
         -0.0355,
         0.95925,
         13274504.88034301,
         0.99459, 0.90661]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    tickers_response = client.tickers(['tIOTBTC', 'tIOTUSD'])
    assert isinstance(tickers_response, list)
    assert tickers_response[0][0] == "tIOTBTC"


def test_ticker_url_is_ok(client, requests_mock):
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text="[]"
    )
    client.ticker('tIOTBTC')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/ticker/tIOTBTC'
    )

def test_ticker_response(client, requests_mock):
    response_text = json.dumps([
        0.00011989,
        224267.1563644,
        0.00012015,
        265388.46405117,
        -8.12e-06,
        -0.0634,
        0.00012,
        3206446.72556849,
        0.00012812,
        0.00011545
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ticker_response = client.ticker('tIOTBTC')
    assert isinstance(ticker_response, (list,))




def test_trades_url_is_ok(client, requests_mock):
    response_text = "[]"
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.trades('tIOTUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/trades/tIOTUSD/hist'
    )

def test_trades_response(client, requests_mock):
    response_text = json.dumps([
        [272147102, 1532428225632, -10.93936053, 0.00012022],
        [272147036, 1532428201910, -260.98846449, 0.00012028]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    trades_response = client.trades('tIOTUSD')
    assert isinstance(trades_response, list)
    assert trades_response[0][0] == 272147102

def test_books_url_is_ok(client, requests_mock):
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text="[]"
    )
    client.books('tIOTUSD', 'P1')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/book/tIOTUSD/P1'
    )

def test_books_response(client, requests_mock):
    response_text = json.dumps([
        [0.97692, 2, 1476.41706974],
        [0.97446, 1, 162.69181129],
        [0.97428, 3, 471.48294762]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    books_response = client.books('tIOTUSD', 'P1')
    assert isinstance(books_response, list)
    assert books_response[0][0] == 0.97692

def test_stats_url_is_ok(client, requests_mock):
    response_text = "[]"
    params = {
        'key'     : 'funding.size',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.stats(**params)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/stats1/funding.size:1m:fUSD/hist?sort=0'
    )

def test_stats_response(client, requests_mock):
    response_text = json.dumps([
        [1532430780000, 548711270.8708785],
        [1532430720000, 546414815.6475447],
        [1532430660000, 545031610.6767836]
    ])
    params = {
        'key'     : 'funding.size',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    stats_response = client.stats(**params)
    assert isinstance(stats_response, list)
    assert stats_response[0][0] == 1532430780000
    assert stats_response[0][1] == 548711270.8708785

def test_candles_url_is_ok(client, requests_mock):
    response_text = json.dumps([
        [1532431320000, 8140.8, 8138.1, 8144, 8138, 15.50046363],
        [1532431260000, 8140.1, 8139.9, 8143.9, 8138.00802545, 29.16099656]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.candles("1m", "tBTCUSD", "hist", limit='1')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist?limit=1'
    )

def test_candles_response(client, requests_mock):
    response_text = json.dumps([
        [1532431320000, 8140.8, 8138.1, 8144, 8138, 15.50046363],
        [1532431260000, 8140.1, 8139.9, 8143.9, 8138.00802545, 29.16099656]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    candles_response = client.candles("1m", "tBTCUSD", "hist", limit='1')
    assert isinstance(candles_response, list)
    assert candles_response[0][0] == 1532431320000
    assert candles_response[0][1] == 8140.8


def test_market_avg_url_is_ok(client, requests_mock):
    response_text = json.dumps([7912.26508244, 100])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.market_average_price(symbol="tBTCUSD", amount="100", period="1m")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/calc/trade/avg'
    )

def test_market_avg_response(client, requests_mock):
    response_text = json.dumps([7912.26508244, 100])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    map_response = client.market_average_price(symbol="tBTCUSD", amount="100", period="1m")
    assert isinstance(map_response, list)
    assert map_response[0] == 7912.26508244
    assert map_response[1] == 100



def test_fx_rate_url_is_ok(client, requests_mock):
    response_text = json.dumps([1.00105])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.foreign_exchange_rate(ccy1="IOT", ccy2="USD")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/calc/fx'
    )


def test_fx_rate_response(client, requests_mock):
    response_text = json.dumps([1.00105])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    map_response = client.foreign_exchange_rate(ccy1="IOT", ccy2="USD")
    assert isinstance(map_response, list)
    assert map_response[0] == 1.00105


def test_wallets_balance_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.wallets_balance()
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/wallets'
    )

def test_wallets_balance_response(client, requests_mock):
    response_text = json.dumps([
        ['funding', 'IOT', 6380, 0, None],
        ['funding', 'OMG', 7.74457581, 0, None],
        ['exchange', 'BAT', 5031.10567614, 0, None],
        ['exchange', 'IOT', 3957.20410603, 0, None],
        ['exchange', 'MNA', 19.05314345, 0, None],
        ['exchange', 'USD', 0.62804524, 0, None],
        ['margin', 'BTC', 0, 0, None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    wb_response = client.wallets_balance()
    assert isinstance(wb_response, list)
    assert wb_response[0][0] == 'funding'
    assert wb_response[0][1] == 'IOT'
    assert wb_response[0][2] == 6380


def test_active_orders_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.active_orders("tIOTUSD")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/orders/tIOTUSD'
    )

def test_active_orders_response(client, requests_mock):
    response_text = json.dumps([
        [13919467011,
         None,
         40580406675,
         'tIOTUSD',
         1530530180426,
         1530530180438,
         -4006.8,
         -4006.8,
         'EXCHANGE LIMIT',
         None,
         None,
         None,
         0,
         'ACTIVE',
         None,
         None,
         8.08,
         0,
         None,
         None,
         None,
         None,
         None,
         0,
         0,
         0,
         None,
         None,
         'API>BFX',
         None,
         None,
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ao_response = client.active_orders("tIOTUSD")
    assert isinstance(ao_response, list)
    assert ao_response[0][3] == 'tIOTUSD'


def test_orders_history_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.orders_history("tIOTUSD")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/orders/tIOTUSD/hist'
    )

def test_orders_history_response(client, requests_mock):
    response_text = json.dumps([
        [14756198784,
         '71',
         688,
         'tIOTUSD',
         1532587404000,
         1532675646000,
         0,
         50.05,
         'EXCHANGE LIMIT',
         None,
         None,
         None,
         None,
         'EXECUTED @ 1.0(50.05)',
         None,
         None,
         1,
         1,
         0,
         0,
         None,
         None,
         None,
         0,
         0,
         None,
         None,
         None,
         'API>BFX',
         None,
         None,
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    oh_response = client.orders_history("tIOTUSD")
    assert isinstance(oh_response, list)
    assert oh_response[0][3] == 'tIOTUSD'


def test_order_trades_url_is_ok(client, requests_mock):
    response_text = json.dumps([
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.order_trades("tIOTUSD", 14395751815)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/order/tIOTUSD:14395751815/trades'
    )

def test_order_trades_response(client, requests_mock):
    response_text = json.dumps([
        [269943238,
         'tIOTUSD',
         1531926144000,
         14463187162,
         50.05,
         1.1272,
         None,
         None,
         1,
         -0.05641636,
         'USD']
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ot_response = client.order_trades("tIOTUSD", 14395751815)
    assert isinstance(ot_response, list)
    assert ot_response[0][1] == 'tIOTUSD'


def test_trades_history_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.trades_history('tIOTUSD', limit=10)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/trades/tIOTUSD/hist'
    )

def test_trades_history_response(client, requests_mock):
    response_text = json.dumps([
        [273186883,
         'tIOTUSD',
         1532675647000,
         14756198784,
         50.05,
         1,
         None,
         None,
         None,
         -0.05005,
         'USD'],
        [273177908,
         'tIOTUSD',
         1532674331000,
         14756270025,
         50.05,
         1.005,
         None,
         None,
         None,
         -0.05030025,
         'USD']
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    th_response = client.trades_history('tIOTUSD', limit=10)
    assert isinstance(th_response, list)
    assert th_response[0][1] == 'tIOTUSD'
    assert th_response[1][1] == 'tIOTUSD'


def test_active_positions_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.active_positions()
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/positions'
    )

def test_active_positions_response(client, requests_mock):
    response_text = json.dumps([
        ['tIOTUSD',
         'ACTIVE',
         4000,
         1.02400594,
         -0.12578296,
         0,
         -193.44454356,
         -4.7227398,
         0.3649879,
         0.8713]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ap_response = client.active_positions()
    assert isinstance(ap_response, list)
    assert ap_response[0][0] == 'tIOTUSD'
    assert ap_response[0][1] == 'ACTIVE'


def test_funding_offers_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_offers("fIOT")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/offers/fIOT'
    )

def test_funding_offers_response(client, requests_mock):
    response_text = json.dumps([
        [277750009,
         'fIOT',
         1532669718000,
         1532669718000,
         30000,
         30000,
         'LIMIT',
         None,
         None,
         0,
         'ACTIVE',
         None,
         None,
         None,
         0.002,
         10,
         0,
         0,
         None,
         0,
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    fo_response = client.funding_offers("fIOT")
    assert isinstance(fo_response, list)
    assert fo_response[0][1] == 'fIOT'
    assert fo_response[0][10] == 'ACTIVE'




def test_funding_offer_history_url(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_offers_history('fOMG')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/offers/fOMG/hist'
    )

def test_funding_offers_hist_resp(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    foh_response = client.funding_offers_history('fOMG')
    assert isinstance(foh_response, list)




def test_funding_loans_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_loans("fIOT")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/loans/fIOT'
    )

def test_funding_loans_response(client, requests_mock):
    response_text = json.dumps([
        [7708021,
         'fOMG',
         1,
         1530761089000,
         1532693100000,
         7.74107199,
         0,
         'ACTIVE',
         None,
         None,
         None,
         0,
         30,
         1530761089000,
         1532693100000,
         0,
         0,
         None,
         0,
         None,
         0]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    fl_response = client.funding_loans("fIOT")
    assert isinstance(fl_response, list)
    assert fl_response[0][1] == 'fOMG'
    assert fl_response[0][7] == 'ACTIVE'



def test_funding_loans_history_url(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_loans_history('fOMG')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/loans/fOMG/hist'
    )

def test_funding_loans_history_resp(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    flh_response = client.funding_loans_history('fOMG')
    assert isinstance(flh_response, list)



def test_funding_credits_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_credits("fIOT")
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/credits/fIOT'
    )

def test_funding_credits_response(client, requests_mock):
    response_text = json.dumps([
        [104425097,
         'fUSD',
         -1,
         1532648567000,
         1532696761000,
         1011.1101,
         0,
         'ACTIVE',
         None,
         None,
         None,
         0.00013245,
         2, 1532648567000,
         1532696761000,
         0,
         0,
         None,
         0,
         None,
         0,
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    fc_response = client.funding_credits("fUSD")
    assert isinstance(fc_response, list)
    assert fc_response[0][1] == 'fUSD'
    assert fc_response[0][7] == 'ACTIVE'


def test_funding_credits_history_url(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_credits_history('fUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/credits/fUSD/hist'
    )

def test_funding_credits_history_resp(client, requests_mock):
    response_text = json.dumps([
        [104187074,
         'fUSD',
         1,
         1532539366000,
         1532589764000,
         518.749995,
         None,
         'CLOSED (reduce_swaps)',
         None,
         None,
         None,
         0.0001109,
         2,
         None,
         None,
         0,
         0,
         None,
         0,
         None,
         0,
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    fch_response = client.funding_credits_history('fUSD')
    assert isinstance(fch_response, list)
    assert fch_response[0][1] == 'fUSD'


def test_funding_trades_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_trades('fUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/funding/trades/fUSD/hist'
    )

def test_funding_trades_response(client, requests_mock):
    response_text = json.dumps([
        [71126559, 'fUSD', 1532690564000, 0, -489.93446, 0.00013558, 2, None],
        [71124554, 'fUSD', 1532689747000, 0, -491.490995, 0.00011935, 2, None],
        [71114966, 'fUSD', 1532683364000, 0, -498.1977, 0.00013667, 2, None],
        [71100173, 'fUSD', 1532676165000, 0, -500.70021, 0.00013111, 2, None],
        [71047501, 'fUSD', 1532653969000, 0, -0.28881967, 0.00014703, 2, None],
        [71034152, 'fUSD', 1532648567000, 0, -1011.1101, 0.00013245, 2, None],
        [70985009, 'fUSD', 1532628548000, 0, -912.55269924, 0.0001188, 2, None],
        [70985008, 'fUSD', 1532628548000, 0, -67.44734076, 0.00011779, 2, None],
        [70869292, 'fUSD', 1532569366000, 0, -0.54663117, 0.0001355, 2, None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ft_response = client.funding_trades('fUSD')
    assert isinstance(ft_response, list)
    assert ft_response[0][1] == 'fUSD'

def test_margin_info_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.margin_info('tIOTUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/info/margin/tIOTUSD'
    )

def test_margin_info_response(client, requests_mock):
    response_text = json.dumps([
        'sym',
        'tIOTUSD',
        [9018.05035061, 14876.97279239, 9018.05035061, 7894.15035061, None, None, None, None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    mi_response = client.margin_info('tIOTUSD')
    assert isinstance(mi_response, list)
    assert mi_response[1] == 'tIOTUSD'
    assert isinstance(mi_response[2], list)


def test_funding_info_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.funding_info('fUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/info/funding/fUSD'
    )

def test_funding_info_response(client, requests_mock):
    response_text = json.dumps([
        'sym',
        'fUSD',
        [0, 0, 1.52802813, 0]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    fi_response = client.funding_info('fUSD')
    assert isinstance(fi_response, list)
    assert fi_response[0] == 'sym'
    assert fi_response[1] == 'fUSD'
    assert isinstance(fi_response[2], list)



def test_movements_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.movements('IOT')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/movements/IOT/hist'
    )

def test_movements_response(client, requests_mock):
    response_text = json.dumps([
        [2550180,
         'IOT',
         'IOTA',
         None,
         None,
         1500445999000,
         1500445999000,
         None,
         None,
         'COMPLETED',
         None,
         None,
         1800,
         0,
         None,
         None,
         'UWDERLMBXDMVVYYLPCGLORYTOTHEROMANEMPIRERBRYANODCLYAFMGFCRULMENTULBARLADSHZDQHCMOMNUVJXGDRS',
         None,
         None,
         None,
         '2550035',
         None]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    m_response = client.movements('IOT')
    assert isinstance(m_response, list)
    assert m_response[0][1] == 'IOT'
    assert m_response[0][9] == 'COMPLETED'


def test_performance_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.performance()
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/stats/perf:1D/hist'
    )


def test_alert_list_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.alert_list()
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/alerts'
    )

def test_alert_list_response(client, requests_mock):
    response_text = json.dumps([
        ['price:tEOSUSD:14.524', 'price', 'tEOSUSD', 14.524, 93],
        ['price:tBTCUSD:6264.3', 'price', 'tBTCUSD', 6264.3, 100],
        ['price:tBCHUSD:713.39', 'price', 'tBCHUSD', 713.39, 100],
        ['price:tBTCUSD:6380.8', 'price', 'tBTCUSD', 6380.8, 94],
        ['price:tBCHUSD:770.08', 'price', 'tBCHUSD', 770.08, 27],
        ['price:tIOTUSD:1.0817', 'price', 'tIOTUSD', 1.0817, 100],
        ['price:tIOTUSD:0.97758', 'price', 'tIOTUSD', 0.97758, 74],
        ['price:tIOTUSD:0.99984', 'price', 'tIOTUSD', 0.99984, 100]
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    al_response = client.alert_list()
    assert isinstance(al_response, list)
    assert al_response[0][2] == 'tEOSUSD'


def test_alert_set_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.alert_set('price', 'tIOTUSD', 1)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/w/alert/set'
    )

def test_alert_set_response(client, requests_mock):
    response_text = json.dumps([
        'price:tIOTUSD:3',
        'price',
        'tIOTUSD',
        3,
        100
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    as_response = client.alert_set('price', 'tIOTUSD', 1)
    assert isinstance(as_response, list)
    assert as_response[2] == 'tIOTUSD'
    assert as_response[3] == 3



def test_alert_delete_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.alert_delete('tIOTUSD', 3)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/w/alert/price:tIOTUSD:3/del'
    )

def test_alert_delete_response(client, requests_mock):
    response_text = json.dumps([True])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    ad_response = client.alert_delete('tIOTUSD', 3)
    assert isinstance(ad_response, list)
    assert ad_response[0]



def test_calc_available_balance_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.calc_available_balance('tIOTUSD', 1, 1.13, 'EXCHANGE')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/calc/order/avail'
    )

def test_calc_available_balance_response(client, requests_mock):
    response_text = json.dumps([0.79734514])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    wb_response = client.calc_available_balance('tIOTUSD', 1, 1.13, 'EXCHANGE')
    assert isinstance(wb_response, list)
    assert wb_response[0] == 0.79734514


def test_ledgers_url_is_ok(client, requests_mock):
    response_text = json.dumps([])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    client.ledgers('IOT')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/auth/r/ledgers/IOT/hist'
    )

def test_ledger_response(client, requests_mock):
    response_text = json.dumps([
        [1772673563,
         'IOT',
         None,
         1532115843000,
         None,
         40,
         2672.7521789,
         None,
         'Transfer of 40.0 IOT from wallet Exchange to Trading on wallet margin'],
        [1772673562,
         'IOT',
         None,
         1532115843000,
         None,
         -40,
         0.81645596,
         None,
         'Transfer of 40.0 IOT from wallet Exchange to Trading on wallet exchange']
    ])
    requests_mock.register_uri(
        rmock.ANY,
        rmock.ANY,
        text=response_text
    )
    l_response = client.ledgers('IOT')
    assert isinstance(l_response, list)
    assert l_response[0][1] == 'IOT'
    assert l_response[1][1] == 'IOT'
