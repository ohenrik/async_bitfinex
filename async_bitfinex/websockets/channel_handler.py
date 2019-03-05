"""Helper for handling multiple channels over one connection"""
from collections.abc import MutableMapping


class ChannelHandler(MutableMapping):

    def __init__(self):
        self.channels = {}

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

    def __getitem__(self, channel_id):
        return self.channels[channel_id]

    def __setitem__(self, future_key, future_object):
        self.futures[future_key] = future_object
        # asyncio.create_task(self.timeout_future(future_key))

    def __delitem__(self, future_key):
        del self.futures[future_key]

    def __iter__(self):
        return iter(self.futures)

    def __len__(self):
        return len(self.futures)
