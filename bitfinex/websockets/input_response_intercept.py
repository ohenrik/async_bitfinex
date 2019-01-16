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
            "n": self.info_message,
            "on": self.order_new_success
        }

    @property
    def info_message_types(self):
        """Lookup table for intercept methods for each message type."""
        return {
            "on-req": self.order_new_request
        }

    def info_message(self, message, futures):
        try:
            # message[2][1] <-- info message type str
            # e.g. "on-req" (request information about new order)
            return self.info_message_types[message[2][1]](message, futures)
        except KeyError:
            return message

    @staticmethod
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
        if message[2][6] != "SUCCESS":
            order_cid = message[2][4][2]
            future_id = f"on_{order_cid}"
            try:
                future = futures[future_id]
                future.set_result({
                    "status": message[2][6], # Error/Sucess
                    "id": message[2][4][0],
                    "cid": order_cid,
                    "response": message[2][4],
                    "comment": message[2][7]
                })
                return False
            except KeyError:
                return message
        return message

    @staticmethod
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
        try:
            future = futures[future_id]
            future.set_result({
                "status": "SUCCESS", # Error/Sucess
                "id": message[2][0],
                "cid": order_cid,
                "response": message[2],
                "comment": None
            })
            return False
        except KeyError:
            return message
