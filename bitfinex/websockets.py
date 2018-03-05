# coding=utf-8
import os
import threading

import time, json
import hmac, hashlib

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning
from bitfinex import wss_utils

# Example used to make send logic
# https://stackoverflow.com/questions/18899515/writing-an-interactive-client-with-twisted-autobahn-websockets

class BitfinexClientProtocol(WebSocketClientProtocol):

    def __init__(self, factory, payload=None):
        self.factory = factory
        self.payload = payload

    def onOpen(self):
        self.factory.protocol_instance = self

    def onConnect(self, response):
        if self.payload:
            self.sendMessage(self.payload, isBinary=False)
        # reset the delay after reconnecting
        self.factory.resetDelay()

    def onMessage(self, payload, isBinary):
        # print("{\n\nMessage Recieved \n\n}")
        if not isBinary:
            try:
                payload_obj = json.loads(payload.decode('utf8'))
            except ValueError:
                pass
            else:
                self.factory.callback(payload_obj)

class BitfinexUserClientProtocol(BitfinexClientProtocol):
    def onConnect(self, response):
        # Send auth message
        self.sendMessage(get_auth_command(), isBinary=False)
        # reset the delay after reconnecting
        self.factory.resetDelay()

class BitfinexReconnectingClientFactory(ReconnectingClientFactory):

    # set initial delay to a short time
    initialDelay = 0.1

    maxDelay = 10

    maxRetries = 5


class BitfinexClientFactory(WebSocketClientFactory, BitfinexReconnectingClientFactory):

    def __init__(self, *args, payload=None, **kwargs):
        WebSocketClientFactory.__init__(self, *args, **kwargs)
        self.protocol_instance = None
        self.base_client = None
        self.payload = payload

    protocol = BitfinexClientProtocol
    _reconnect_error_payload = {
        'e': 'error',
        'm': 'Max reconnect retries reached'
    }

    def clientConnectionFailed(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)

    def clientConnectionLost(self, connector, reason):
        self.retry(connector)
        if self.retries > self.maxRetries:
            self.callback(self._reconnect_error_payload)

    def buildProtocol(self, addr):
        return BitfinexClientProtocol(self, payload=self.payload)

class BitfinexUserClientFactory(BitfinexClientFactory, BitfinexReconnectingClientFactory):

    protocol = BitfinexUserClientProtocol

    def buildProtocol(self, addr):
        return BitfinexUserClientProtocol(self)

class BitfinexSocketManager(threading.Thread):

    STREAM_URL = 'wss://api.bitfinex.com/ws/2'

    _user_timeout = 30 * 60  # 30 minutes

    def __init__(self): #client
        """Initialise the BitfinexSocketManager
        :param client: Bitfinex API client
        :type client: binance.Client
        """
        threading.Thread.__init__(self)
        # self.auth_factory = None
        self.factories = {}
        self._connected_event = threading.Event()
        self._conns = {}
        self._user_timer = None
        self._user_listen_key = None
        self._user_callback = None

    # def _start_user_socket(self, callback):
    #     if "user" in self._conns:
    #         return False
    #
    #     factory_url = self.STREAM_URL
    #     self.auth_factory = BitfinexUserClientFactory(factory_url)
    #     self.auth_factory.base_client = self
    #     self.auth_factory.protocol = BitfinexUserClientProtocol
    #     self.auth_factory.callback = callback
    #     # factory.json
    #     self.auth_factory.reconnect = True
    #     context_factory = ssl.ClientContextFactory()
    #
    #     self._conns["user"] = connectWS(self.auth_factory, context_factory)
    #     return self._conns["user"]

    def _start_socket(self, id_, payload, callback):
        if id_ in self._conns:
            return False

        factory_url = self.STREAM_URL
        factory = BitfinexClientFactory(factory_url, payload=payload)
        factory.base_client = self
        factory.protocol = BitfinexClientProtocol
        factory.callback = callback
        factory.reconnect = True
        context_factory = ssl.ClientContextFactory()
        self.factories[id_] = factory
        self._conns[id_] = connectWS(factory, context_factory)
        return self._conns[id_]

    def stop_socket(self, conn_key):
        """Stop a websocket given the connection key
        :param conn_key: Socket connection key
        :type conn_key: string
        :returns: connection key string if successful, False otherwise
        """
        if conn_key not in self._conns:
            return

        # disable reconnecting if we are closing
        self._conns[conn_key].factory = WebSocketClientFactory(self.STREAM_URL)
        self._conns[conn_key].disconnect()
        del(self._conns[conn_key])


    def run(self):
        try:
            reactor.run(installSignalHandlers=False)
        except ReactorAlreadyRunning:
            # Ignore error about reactor already running
            pass

    def close(self):
        """Close all connections
        """
        keys = set(self._conns.keys())
        for key in keys:
            self.stop_socket(key)

        self._conns = {}

    ###########################################################################
    # Bitfinex commands
    ###########################################################################

    def authenticate(self, callback, filters=None):
        nonce = int(time.time() * 1000000)
        auth_payload = 'AUTH{}'.format(nonce)
        signature = hmac.new(
            os.environ.get("API_SECRET").encode(), #settings.API_SECRET.encode()
            msg = auth_payload.encode('utf8'),
            digestmod = hashlib.sha384
        ).hexdigest()
        data = {
            # docs: http://bit.ly/2CEx9bM
            'event': 'auth',
            'apiKey': os.environ.get("API_KEY"),
            'authSig': signature,
            'authPayload': auth_payload,
            'authNonce': nonce,
            'calc': 1
        }
        if filters:
            data['filter'] = filters
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        return self._start_socket("auth", payload, callback)


    def subscribe_to_candles(self, pair, timeframe, callback):
        """Subscribe to the passed pair's OHLC data channel.
        :param pair: str, Symbol pair to request data for
        :param timeframe: str, {1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h,
                                1D, 7D, 14D, 1M}
        :param kwargs:
        :return:
        """

        valid_tfs = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D',
                     '7D', '14D', '1M']
        if timeframe:
            if timeframe not in valid_tfs:
                raise ValueError("timeframe must be any of %s" % valid_tfs)
        else:
            timeframe = '1m'
        identifier = ('candles', pair, timeframe)
        id_ = "_".join(identifier)
        pair = 't' + pair if not pair.startswith('t') else pair
        key = 'trade:' + timeframe + ':' + pair
        data = {
            'event': 'subscribe',
            'channel': 'candles',
            'key': key,
        }
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        return self._start_socket(id_, payload, callback)

    def new_order(self, order_type, pair, amount, price, hidden=0):
        # assert order_type in wss_utils.ORDER_TYPES, (
        #     "{}: is not a valid order type".format(order_type))
        data = [
            0,
            wss_utils.get_notification_code('new order'),
            None,
            {
                # docs: http://bit.ly/2CrQjWO
                'cid': time.time()*1000,
                'type': order_type,
                'symbol': wss_utils.order_pair(pair),
                'amount': amount,
                'price': price,
                'hidden': hidden
            }
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)

    def cancel_order(self, order_id):
        data = [
            0,
            wss_utils.get_notification_code('cancel order'),
            None,
            {
                # docs: http://bit.ly/2BVqwW6
                'id': order_id
            }
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)
