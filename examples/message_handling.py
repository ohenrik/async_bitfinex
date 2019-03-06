import asyncio
import traceback
from async_bitfinex import WssClient

def handle_channel_exception(loop, context):
    """All exceptions are set to stop the entire event loop"""
    # logging.error(context)
    traceback.print_tb(context["exception"].__traceback__)
    traceback.print_exc()
    loop.stop()

def ignore_message(_):
    """Method designed to do nothing. Simplifies handling ignored messages"""
    pass

def get_auth_message_type(message):
    """Reads raw auth channel messages and extracts the message type and
    message body"""
    if isinstance(message, list) and message[1] == "hb":
        message_type = "hb"
    elif isinstance(message, list):
        message = message[2] if message[1] == "n" else message
        # message[1] <-- message type str, e.g. "on" (successfull new order)
        message_type = message[1]
    else:
        message_type = message["event"]
    return message_type, message

def get_book_message_type(message):
    """Reads raw orderbook channel messages and extracts the message type and
    message body"""
    if isinstance(message, list) and message[1] == "hb":
        message_type = "hb"
    elif isinstance(message, list) and isinstance(message[1][0], list):
        message_type = "snapshot"
    elif isinstance(message, list) and len(message[1]) >= 2:
        message_type = "update"
    else:
        message_type = message["event"]
    return message_type, message

class MyClass:

    def __init__(self):
        self.client = WssClient()
        asyncio.get_event_loop().set_exception_handler(
            handle_channel_exception
        )

    @property
    def book_message_handlers(self):
        """A desicion table for websocket message handlers"""
        return {
            "snapshot": self._handle_book_snapshot,
            "update": self._handle_book_update,
        }

    # @property
    # def auth_message_handlers(self):
    #     """A desicion table for websocket message handlers"""
    #     return {
    #         "auth": self._auth_success_handler,
    #         "error": self._error_handler,
    #     }

    async def _handle_book_message(self, message):
        """This is the book callback method. It triggers all other methods
        based on its type."""
        message_type, message = get_book_message_type(message)
        self.book_message_handlers.get(message_type, ignore_message)(message)

    async def _handle_auth_message(self, message):
        """This is the auth callback method. It triggers all other methods
        based on its type."""
        message_type, message = get_auth_message_type(message)
        self.auth_message_handlers.get(message_type, ignore_message)(message)

    def _handle_book_update(self, message):
        """Handle Updates"""
        pair = self.client.channels[message[0]]["pair"]
        symbol = self.client.channels[message[0]]["symbol"]
        resolution = self.client.channels[message[0]]["res"]
        length = self.client.channels[message[0]]["len"]
        # Do things here

    def _handle_book_snapshot(self, message):
        """Handle snapshots"""
        pair = self.client.channels[message[0]]["pair"]
        symbol = self.client.channels[message[0]]["symbol"]
        resolution = self.client.channels[message[0]]["res"]
        length = self.client.channels[message[0]]["len"]
        # Do things here
