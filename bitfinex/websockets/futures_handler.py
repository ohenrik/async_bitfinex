"""Module for logic related to intercepting input responses over the bitfinex
auth channel"""
import asyncio
from collections.abc import MutableMapping

def order_new_request(message, futures):
    """Intercepts order new request info messages (on-req) and handles
    potential request errors.

    If none are found it returns the message unchanged to be handled by the
    default auth callback.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    order_cid = message[4][2]
    future_id = f"on-req_{order_cid}"
    futures[future_id].set_result({
        "status": message[6], # Error/Sucess
        "id": message[4][0],
        "cid": order_cid,
        "response": message[4],
        "comment": message[7]
    })
    del futures[future_id]

def order_cancel_request(message, futures):
    """Intercepts order new request info messages (on-req) and handles
    potential request errors.

    If none are found it returns the message unchanged to be handled by the
    default auth callback.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    order_cid = message[4][2]
    future_id = f"oc-req_{order_cid}"
    futures[future_id].set_result({
        "status": message[6], # Error/Sucess
        "id": message[4][0],
        "cid": order_cid,
        "response": message[4],
        "comment": message[7]
    })
    del futures[future_id]


def order_new_success(message, futures):
    """Intercepts order new (on) messages and check for awaited futures.
    If none are found it returns the message unchanged to be handled by the
    default auth callback.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}

    """
    order_cid = message[2][2]
    future_id = f"on_{order_cid}"
    future = futures[future_id]
    future.set_result({
        "status": "SUCCESS", # Error/Sucess
        "id": message[2][0],
        "cid": order_cid,
        "response": message[2],
        "comment": None
    })
    del futures[future_id]

def order_cancel_success(message, futures):
    """Intercepts order cancel (oc) messages and check for awaited futures.
    If none are found it returns the message unchanged to be handled by the
    default auth callback.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}

    """
    order_cid = message[2][2] or message[2][0] # uses id, if no cid given
    future_id = f"oc_{order_cid}"
    future = futures[future_id]
    future.set_result({
        "status": "SUCCESS", # Error/Sucess
        "id": message[2][0],
        "cid": message[2][2],
        "response": message[2],
        "comment": None
    })
    del futures[future_id]



class FuturesHandler(MutableMapping):

    def __init__(self, timeout_seconds=10, message_handlers=None):
        self.futures = {}
        self.timeout_seconds = timeout_seconds
        self._message_handlers = {
            # "n": self.info_message,
            "on-req": order_new_request,
            "oc-req": order_cancel_request,
            # "auth": self.auth_event,
            "on": order_new_success,
            "oc": order_cancel_success,
            **(message_handlers if message_handlers else {})
        }
        # TODO: Create logic to remove futures taht are Done or TimedOut

    def __call__(self, message):
        """Try to handle/intercept messages to set results for awaited
        future objects

        Parameters
        ----------
        message : str
            The unaltered response message returned by bitfinex.
        futures : dict
            A dict of intercept_id's and future objects.
            dict{intercept_id, future_object}
        """
        try:
            message_type, message = self.get_message_type(message)
            return self.message_types[message_type](message, self.futures)
        except (KeyError, TypeError):
            pass

    def __getitem__(self, future_key):
        return self.futures[future_key]

    def __setitem__(self, future_key, future_object):
        self.futures[future_key] = future_object
        # asyncio.create_task(self.timeout_future(future_key))

    def __delitem__(self, future_key):
        del self.futures[future_key]

    def __iter__(self):
        return iter(self.futures)

    def __len__(self):
        return len(self.futures)

    @staticmethod
    def get_message_type(message):
        if isinstance(message, list):
            message = message[2] if message[1] == "n" else message
            # message[1] <-- message type str, e.g. "on" (successfull new order)
            message_type = message[1]
        else:
            message_type = message["event"]
        return message_type, message

    @property
    def message_types(self):
        """Lookup table for intercept methods for each message type."""
        return self._message_handlers
