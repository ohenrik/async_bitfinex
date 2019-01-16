"""Module for logic related to intercepting input responses over the bitfinex
auth channel"""


class InputResponseInterceptor:

    def __call__(self, message, futures):
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
            # message[1] <-- message type str, e.g. "on" (successfull new order)
            return self.message_types[message[1]](message, futures)
        except KeyError:
            return message

    @property
    def message_types(self):
        """Lookup table for intercept methods for each message type."""
        return {
            # "n": "test",
            "on": self.order_new
        }

    # INFO_MESSAGE_TYPES = {
    #     "on-req": "test"
    # }

    @staticmethod
    def order_new(message, futures):
        """Intercepts order new (on) messages and check for awaited futuresself.
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
        message_type = "on"
        order_cid = message[2][2]
        future_id = f"{message_type}_{order_cid}"
        try:
            future = futures[future_id]
            future.set_result(message)
            return False
        except KeyError:
            return message
