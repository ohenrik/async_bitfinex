"""Module for rest and websocket utilities"""
import time
from datetime import datetime

def create_cid():
    """Create a new Client order id. Based on timestamp multiplied to 100k to
    make it improbable that two actions are assigned the same cid."""
    now = datetime.utcnow()
    return int(float(now.strftime("%s.%f"))*10000000)

def cid_to_date(cid):
    """Converts a cid to date string YYYY-MM-DD"""
    return datetime.utcfromtimestamp(
        cid/10000000.0
    ).strftime("%Y-%m-%d")

def get_nonce(multiplier):
    """
        Returns a nonce used in authentication.
        Nonce must be an increasing number.
        If other frameworks have used higher numbers you might
        need to increase the nonce_multiplier.
    """
    return str(float(time.time()) * multiplier)

def order_symbol(symbol):
    symbol = 't' + symbol if not symbol.startswith('t') else symbol
    return symbol
