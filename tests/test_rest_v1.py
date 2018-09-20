# pylint: disable=W0621,C0111
import os
from decouple import config
import json
import pytest
import requests_mock as rm
from bitfinex.rest import ClientV1 as Client


API_KEY = "test" #os.environ.get('API_KEY', config('API_KEY'))
API_SECRET = "test" #os.environ.get('API_SECRET', config('API_SECRET'))

@pytest.fixture()
def client():
    return Client(key="testing", secret="testing")


def test_should_have_server(client):
    assert client.server() == "https://api.bitfinex.com/v1"


def test_should_have_url_for_foo(client):
    assert client.url_for("foo") == "https://api.bitfinex.com/v1/foo"


def test_should_have_url_for_path_arg(client):
    assert client.url_for('foo/%s', path_arg="bar") == (
        "https://api.bitfinex.com/v1/foo/bar"
    )


def test_should_have_url_with_parameters(client):
    assert client.url_for('foo', parameters={'a': 1, 'b': 2}) == (
        "https://api.bitfinex.com/v1/foo?a=1&b=2"
    )

def test_should_have_url_for(client):
    assert client.url_for("foo") == "https://api.bitfinex.com/v1/foo"


def test_should_have_url_for_with_path_arg(client):
    expected = "https://api.bitfinex.com/v1/foo/bar"
    path = "foo/%s"
    assert client.url_for(path, path_arg='bar') == expected
    assert client.url_for(path, 'bar') == expected


def test_should_have_url_for_with_parameters(client):
    expected = "https://api.bitfinex.com/v1/foo?a=1"
    assert client.url_for("foo", parameters={'a': 1}) == expected
    assert client.url_for("foo", None, {'a': 1}) == expected


def test_should_have_url_for_with_path_arg_and_parameters(client):
    expected = "https://api.bitfinex.com/v1/foo/bar?a=1"
    path = "foo/%s"
    assert client.url_for(path, path_arg='bar', parameters={'a': 1}) == expected
    assert client.url_for(path, 'bar', {'a': 1}) == expected


def test_should_have_symbols(client, requests_mock):
    request_result = ["btcusd", "ltcusd", "ltcbtc"]
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text='["btcusd", "ltcusd", "ltcbtc"]'
    )
    assert client.symbols() == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/symbols'
    )

def test_should_have_symbol_details(client, requests_mock):
    # mock out the request
    request_result = '''[{
        "pair":"btcusd",
        "price_precision":5,
        "initial_margin":"30.0",
        "minimum_margin":"15.0",
        "maximum_order_size":"2000.0",
        "minimum_order_size":"0.01",
        "expiration":"NA"
        },{
        "pair":"ltcusd",
        "price_precision":5,
        "initial_margin":"30.0",
        "minimum_margin":"15.0",
        "maximum_order_size":"5000.0",
        "minimum_order_size":"0.1",
        "expiration":"NA"
        }]'''
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=request_result
    )
    result = client.symbols_details()
    assert result == json.loads(request_result)
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/symbols_details'
    )


def test_should_have_ticker(client, requests_mock):
    # mock out the request
    request_result = {
        "mid": "562.56495",
        "bid": "562.15",
        "ask": "562.9799",
        "last_price": "562.25",
        "volume": "7842.11542563",
        "timestamp": "1395552658.339936691"
    }
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.ticker('btcusd') == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/pubticker/btcusd'
    )


def test_should_have_today(client, requests_mock):
    # mock out the request
    request_result = {"low":"550.09","high":"572.2398","volume":"7305.33119836"}
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )

    assert client.today('btcusd') == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/today/btcusd'
    )


def test_should_have_stats(client, requests_mock):
    request_result = [
        {"period":1, "volume":"7410.27250155"},
        {"period":7, "volume":"52251.37118006"},
        {"period":30, "volume":"464505.07753251"}
    ]
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.stats('btcusd') == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/stats/btcusd'
    )

def test_should_have_lendbook(client, requests_mock):
    request_result = {
        "bids":[
            {"rate":"5.475", "amount":"15.03894663", "period":30,
             "timestamp":"1395112149.0", "frr": False},
            {"rate":"2.409", "amount":"14.5121868", "period":7,
             "timestamp":"1395497599.0", "frr":False}
        ],
        "asks":[
            {"rate":"6.351", "amount":"15.5180735", "period":5,
             "timestamp":"1395549996.0", "frr":False},
            {"rate":"6.3588", "amount":"626.94808249", "period":30,
             "timestamp":"1395400654.0", "frr": False}
        ]
    }
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.lendbook('btc') == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/lendbook/btc'
    )


def test_should_have_lendbook_with_parameters(client, requests_mock):
    request_result = '{"bids":[{"rate":"5.475","amount":"15.03894663","period":30,\
        "timestamp":"1395112149.0","frr":"No"},{"rate":"2.409",\
        "amount":"14.5121868","period":7,"timestamp":"1395497599.0",\
        "frr":"No"}],"asks":[]}'
    parameters = {'limit_bids': 2, 'limit_asks': 0}
    expected = {
        "bids": [
            {"rate": "5.475", "amount": "15.03894663", "period": 30,
             "timestamp": "1395112149.0", "frr": False},
            {"rate": "2.409", "amount": "14.5121868", "period": 7,
             "timestamp": "1395497599.0", "frr": False}
        ],
        "asks": []
    }
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=request_result
    )
    assert client.lendbook('btc', parameters) == expected
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/lendbook/btc?limit_asks=0&limit_bids=2'
    )

def test_should_have_order_book(client, requests_mock):
    request_result = {
        "bids": [
            {"price": "562.2601", "amount": "0.985", "timestamp": "1395567556.0"}
        ],
        "asks": [
            {"price": "563.001", "amount": "0.3", "timestamp": "1395532200.0"}
        ]
    }
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.order_book('btcusd') == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/book/btcusd'
    )

def test_should_have_order_book_with_parameters(client, requests_mock):
    parameters = {'limit_asks': 0}
    request_result = {
        "bids": [
            {"price": "562.2601", "amount": "0.985", "timestamp": "1395567556.0"}
        ],
        "asks": []
    }

    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.order_book('btcusd', parameters) == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/book/btcusd?limit_asks=0'
    )


def test_get_active_orders_returns_json(client, requests_mock):
    request_result = [{
        "price":"562.2601",
        "amount":"0.985",
        "timestamp":"1395567556.0"
    }]
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.active_orders() == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/orders'
    )

def test_get_active_positions_returns_json(client, requests_mock):
    request_result = [{
        "price":"562.2601",
        "amount":"0.985",
        "timestamp":"1395567556.0"
    }]
    requests_mock.register_uri(
        rm.ANY,
        rm.ANY,
        text=json.dumps(request_result)
    )
    assert client.active_positions() == request_result
    assert requests_mock.request_history[0].url == (
        'https://api.bitfinex.com/v1/positions'
    )

# def test_get_full_history(client, requests_mock):
#     mock_body = [{
#         "price":"562.2601",
#         "amount":"0.985",
#         "timestamp":"1395567556.0"
#     }]
#     url = client.url_for(path="orders")
#     httpretty.register_uri(httpretty.POST, url, body=mock_body, status=200)
#
#     ap = client.active_positions()
#     self.assertIsInstance(ap, list)
