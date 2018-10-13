import pytest
from bitfinex import utils

def test_order_symbol_adds_t_to_symbol():
    assert utils.order_symbol("BTCUSD") == "tBTCUSD"

def test_order_symbol_keeps_t_to_symbol():
    assert utils.order_symbol("tBTCUSD") == "tBTCUSD"

def test_order_symbol_adds_t_to_symbol_lowercase():
    assert utils.order_symbol("btcusd", capital=False) == "tbtcusd"

def test_order_symbol_adds_f_to_symbol():
    assert utils.order_symbol("BTC") == "fBTC"

def test_order_symbol_keeps_f_to_symbol():
    assert utils.order_symbol("fBTC") == "fBTC"

def test_order_symbol_adds_f_to_symbol_lowercase():
    assert utils.order_symbol("btc", capital=False) == "fbtc"

def test_order_symbol_capital_letters():
    assert utils.order_symbol("btcusd") == "tBTCUSD"

def test_order_symbol_passes_on_unknown_symbols_unchanged():
    assert utils.order_symbol("custom_sym") == "custom_sym"
