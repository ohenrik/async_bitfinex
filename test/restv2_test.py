"""Tests for the v2 rest api"""
import json
import pytest
import requests_mock as rm
from bitfinex.rest.restv2 import Client

# pylint: disable=W0621,C0111

@pytest.fixture
def client():
    return Client()

def test_ticker_url_is_correct(client, requests_mock):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text="[]"
    )
    client.ticker('tIOTBTC')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/ticker/tIOTBTC'
    )

def test_ticker_response_is_parsed(client, requests_mock):
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
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    ticker_response = client.ticker('tIOTBTC')
    assert isinstance(ticker_response, (list,))

def test_platform_status(client, requests_mock):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text='[1]'
    )
    platform_status = client.platform_status()
    assert platform_status == [1]

def test_tickers_url_is_correct(client, requests_mock):
    """test method 2/34 tickers"""
    response_text = "[]"
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    client.tickers(['tIOTBTC', 'tIOTUSD'])
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/tickers?symbols=tIOTBTC,tIOTUSD'
    )

def test_tickers_response_is_parsed(client, requests_mock):
    """test method 2/34 tickers"""
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
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    tickers_response = client.tickers(['tIOTBTC', 'tIOTUSD'])
    assert isinstance(tickers_response, list)
    assert tickers_response[0][0] == "tIOTBTC"

def test_trades_url_is_correct(client, requests_mock):
    response_text = "[]"
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    client.trades('tIOTUSD')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/trades/tIOTUSD/hist'
    )

def test_trades_response_is_parsed(client, requests_mock):
    response_text = json.dumps([
        [272147102, 1532428225632, -10.93936053, 0.00012022],
        [272147036, 1532428201910, -260.98846449, 0.00012028]
    ])
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    trades_response = client.trades('tIOTUSD')
    assert isinstance(trades_response, list)
    assert trades_response[0][0] == 272147102

def testm_books_url_is_correct(client, requests_mock):
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text="[]"
    )
    client.books('tIOTUSD', 'P1')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/book/tIOTUSD/P1'
    )

def test_books_response_is_parsed(client, requests_mock):
    response_text = json.dumps([
        [0.97692, 2, 1476.41706974],
        [0.97446, 1, 162.69181129],
        [0.97428, 3, 471.48294762]
    ])
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    books_response = client.books('tIOTUSD', 'P1')
    assert isinstance(books_response, list)
    assert books_response[0][0] == 0.97692

def test_stats_url_is_correct(client, requests_mock):
    response_text = "[]"
    params = {
        'key'     : 'funding.size',
        'size'    : '1m',
        'symbol'  : 'fUSD',
        'section' : 'hist',
        'sort'    : '0'
    }
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    stats_response = client.stats(**params)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/stats1/funding.size:1m:fUSD/hist?sort=0'
    )

def test_stats_response_is_parsed(client, requests_mock):
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
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    stats_response = client.stats(**params)
    assert isinstance(stats_response, list)
    assert stats_response[0][0] == 1532430780000
    assert stats_response[0][1] == 548711270.8708785

def test_candles_url_is_correct(client, requests_mock):
    response_text = json.dumps([
        [1532431320000, 8140.8, 8138.1, 8144, 8138, 15.50046363],
        [1532431260000, 8140.1, 8139.9, 8143.9, 8138.00802545, 29.16099656]
    ])
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    client.candles("1m", "tBTCUSD", "hist", limit='1')
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v2/candles/trade:1m:tBTCUSD/hist?limit=1'
    )

def test_candles_response_is_parsed(client, requests_mock):
    response_text = json.dumps([
        [1532431320000, 8140.8, 8138.1, 8144, 8138, 15.50046363],
        [1532431260000, 8140.1, 8139.9, 8143.9, 8138.00802545, 29.16099656]
    ])
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=response_text
    )
    candles_response = client.candles("1m", "tBTCUSD", "hist", limit='1')
    assert isinstance(candles_response, list)
    assert candles_response[0][0] == 1532431320000
    assert candles_response[0][1] == 8140.8
