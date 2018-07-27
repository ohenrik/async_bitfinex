"""Bitfinex main module"""
from .rest.restv1 import Client
from .rest.restv2 import Client as ClientV2
from .websockets.client import WssClient

# This is for packward compatability.
ClientV1 = Client
