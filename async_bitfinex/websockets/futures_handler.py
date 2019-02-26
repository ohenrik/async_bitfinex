"""Module for logic related to intercepting input responses over the bitfinex
auth channel"""
from collections.abc import MutableMapping
import asyncio
from asyncio import InvalidStateError, CancelledError

def pong_handler(message, futures):
    """Intercepts ping messages (pong) and check for
    Future objets with a matching cid.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    order_cid = message["cid"]
    future_id = f"pong_{order_cid}"
    futures[future_id].set_result(message)
    del futures[future_id]

def order_new_request(message, futures):
    """Intercepts order new request info messages (on-req) and check for
    Future objets with a matching cid.

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

def order_update_request(message, futures):
    """Intercepts order update request info messages (ou-req) and check for
    Future objets with a matching cid.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    order_id = message[4][0]
    future_id = f"ou-req_{order_id}"
    futures[future_id].set_result({
        "status": message[6], # Error/Sucess
        "id": message[4][0],
        "cid": message[4][2],
        "response": message[4],
        "comment": message[7]
    })
    del futures[future_id]

def order_cancel_request(message, futures):
    """Intercepts order cancel request info messages (oc-req) and check for
    Future objets with a matching cid.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    order_cid = message[4][2] or message[4][0]
    future_id = f"oc-req_{order_cid}"
    futures[future_id].set_result({
        "status": message[6], # Error/Sucess
        "id": message[4][0],
        "cid": message[4][2],
        "response": message[4],
        "comment": message[7]
    })
    del futures[future_id]


def order_new_success(message, futures):
    """Intercepts order new (on) messages and check for Future objets with
    a matching cid.

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

def order_update_success(message, futures):
    """Intercepts order new (on) messages and check for Future objets with
    a matching cid.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}

    """
    order_id = message[2][0]
    future_id = f"ou_{order_id}"
    future = futures[future_id]
    future.set_result({
        "status": "SUCCESS", # Error/Sucess
        "id": message[2][0],
        "cid": message[2][2],
        "response": message[2],
        "comment": None
    })
    del futures[future_id]

def order_cancel_success(message, futures):
    """Intercepts order cancel messages (oc) and check for
    Future objets with a matching cid.

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

def subscription_confirmations(message, futures):
    """Intercepts subscribe messages and check for
    Future objets with a matching subscribe details.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    if message["channel"] in ("trades", "book", "ticker"):
        future_id = f"{message['channel']}_{message['symbol']}"
        futures[future_id].set_result(message)
        del futures[future_id]
    elif message["channel"] == "candles":
        future_id = f"candles_{message['key']}"
        futures[future_id].set_result(message)
        del futures[future_id]

def unsubscribe_confirmations(message, futures):
    """Intercepts unsubscribe messages and check for
    Future objets with a matching subscribe details.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    future_id = f"unsubscribe_{message['chanId']}"
    futures[future_id].set_result(message)
    del futures[future_id]

def auth_confirmation(message, futures):
    """Intercepts auth messages and check for
    Future objets with a matching auth details.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    future = futures["auth"]
    future.set_result(message)
    del futures["auth"]

def error_handler(message, futures):
    """Intercepts error messages and check for
    Future objets with a matching subscribe details.

    Parameters
    ----------
    message : str
        The unaltered response message returned by bitfinex.
    futures : dict
        A dict of intercept_id's and future objects.
        dict{intercept_id, future_object}
    """
    if "unsubscribe" in message["msg"]:
        unsubscribe_confirmations(message, futures)
    elif "subscribe" in message["msg"]:
        subscription_confirmations(message, futures)

CLIENT_HANDLERS = {
    "subscribed": subscription_confirmations,
    "unsubscribed": unsubscribe_confirmations,
    "auth": auth_confirmation,
    "error": subscription_confirmations,
    "on-req": order_new_request,
    "ou-req": order_update_request,
    "oc-req": order_cancel_request,
    "pong": pong_handler,
    "on": order_new_success,
    "ou": order_update_success,
    "oc": order_cancel_success,
    # **(message_handlers if message_handlers else {})
}

class FuturesHandler(MutableMapping):
    """Handles Future objects and sets results when matching
    responses are found.

    Parameters
    ----------
    message_handlers : dict
        A dictionary containing message handle functions used to react to
        incomming responses (messages) and set the result of Future objects.
        Se `order_new_request` above as example.
    """

    def __init__(self, message_handlers=None, futures_cleanup_interval=10):
        self.futures = {}
        self._message_handlers = message_handlers
        self.futures_cleanup_interval = futures_cleanup_interval
        asyncio.get_event_loop().create_task(self.clear_expired_futures())

    async def clear_expired_futures(self):
        await asyncio.sleep(self.futures_cleanup_interval)
        delete_keys = []
        for future_id, future in self.futures.items():
            try:
                is_complete = any([
                    future.done(),
                    future.cancelled(),
                    future.exception() == TimeoutError
                ])
                if is_complete:
                    delete_keys.append(future_id)
            except (InvalidStateError, CancelledError):
                pass
        for future_id in delete_keys:
            del self.futures[future_id]
        asyncio.get_event_loop().create_task(self.clear_expired_futures())

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
        # Exit immidiatly if there are no futures to handle
        if not self.futures:
            return
        try:
            message_type, message = self._get_message_type(message)
            return self._message_handlers[message_type](message, self.futures)
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
    def _get_message_type(message):
        if isinstance(message, list) and message[0] == 0:
            message = message[2] if message[1] == "n" else message
            # message[1] <-- message type str, e.g. "on" (successfull new order)
            message_type = message[1]
        elif isinstance(message, list) and message[0] > 0:
            message_type = "update"
        else:
            message_type = message["event"]
        return message_type, message
