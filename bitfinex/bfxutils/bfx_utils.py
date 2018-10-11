"""Module for rest and websocket utilities"""
import time


def get_nonce(multiplier):
    """
        Returns a nonce used in authentication.
        Nonce must be an increasing number.
        If other frameworks have used higher numbers you might
        need to increase the nonce_multiplier.
    """
    return str(float(time.time()) * multiplier)
