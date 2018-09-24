# coding=utf-8
import os
import threading
from datetime import date
import json
import hmac, hashlib

from autobahn.twisted.websocket import WebSocketClientFactory, \
    WebSocketClientProtocol, \
    connectWS
from twisted.internet import reactor, ssl
from twisted.internet.protocol import ReconnectingClientFactory
from twisted.internet.error import ReactorAlreadyRunning
from bitfinex.websockets import wss_utils

# Example used to make send logic
# https://stackoverflow.com/questions/18899515/writing-an-interactive-client-with-twisted-autobahn-websockets

class BitfinexClientProtocol(WebSocketClientProtocol):

    def __init__(self, factory, payload=None):
        super().__init__()
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
        if not isBinary:
            try:
                payload_obj = json.loads(payload.decode('utf8'))
            except ValueError:
                pass
            else:
                self.factory.callback(payload_obj)

class BitfinexReconnectingClientFactory(ReconnectingClientFactory):

    # set initial delay to a short time
    initialDelay = 0.1

    maxDelay = 20

    maxRetries = 30


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


class BitfinexSocketManager(threading.Thread):

    STREAM_URL = 'wss://api.bitfinex.com/ws/2'

    def __init__(self): #client
        """Initialise the BitfinexSocketManager"""
        threading.Thread.__init__(self)
        self.factories = {}
        self._connected_event = threading.Event()
        self._conns = {}
        self._user_timer = None
        self._user_listen_key = None
        self._user_callback = None

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
        reactor.callFromThread(self.add_connection, id_)


    def add_connection(self, id_):
        """
        Convenience function to connect and store the resulting
        connector.
        """
        factory = self.factories[id_]
        context_factory = ssl.ClientContextFactory()
        self._conns[id_] = connectWS(factory, context_factory)


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


class WssClient(BitfinexSocketManager):

    ###########################################################################
    # Bitfinex commands
    ###########################################################################

    def __init__(self, key=None, secret=None): #client
        """Initialise the WssClient"""
        super().__init__()
        self.key = key
        self.secret = secret

    def authenticate(self, callback, filters=None):
        nonce = int(wss_utils.UtcNow() * 1000000)
        auth_payload = 'AUTH{}'.format(nonce)
        signature = hmac.new(
            self.secret.encode(), #settings.API_SECRET.encode()
            msg=auth_payload.encode('utf8'),
            digestmod=hashlib.sha384
        ).hexdigest()
        data = {
            # docs: http://bit.ly/2CEx9bM
            'event': 'auth',
            'apiKey': self.key,
            'authSig': signature,
            'authPayload': auth_payload,
            'authNonce': nonce,
            'calc': 1
        }
        if filters:
            data['filter'] = filters
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket("auth", payload, callback)

    def subscribe_to_ticker(self, symbol, callback):
        """Subscribe to the passed symbol ticks data channel.
        """
        symbol = 't' + symbol if not symbol.startswith('t') else symbol
        id_ = "_".join(["ticker", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'ticker',
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, callback)

    def subscribe_to_trades(self, symbol, callback):
        """Subscribe to the passed symbol trades data channel.
        """
        symbol = 't' + symbol if not symbol.startswith('t') else symbol
        id_ = "_".join(["trades", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'trades',
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        return self._start_socket(id_, payload, callback)

    #Precision: R0, P0, P1, P2, P3
    def subscribe_to_orderbook(self, symbol, precision, callback):
        """Subscribe to the orderbook of a given pair.

        Parameters
        ----------
        symbol : str
            Symbol pair to request data for.

        precision : str
            Accepted values as strings {R0, P0, P1, P2, P3}

        callback : func
            A function to use as callback
        """
        symbol = 't' + symbol if not symbol.startswith('t') else symbol
        id_ = "_".join(["order", symbol])
        data = {
            'event': 'subscribe',
            "channel": "book",
            "prec": precision,
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        return self._start_socket(id_, payload, callback)

    # TODO: Switch "pair" to "symbol" in new major version
    def subscribe_to_candles(self, pair, timeframe, callback):
        """Subscribe to the passed pair's OHLC data channel.

        Parameters
        ----------
        pair : str
            Symbol pair to request data for

        timeframe : str
            Accepted values as strings {1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h,
            1D, 7D, 14D, 1M}

        callback : func
            A function to use as callback

        Returns
        -------
        str
            The socket identifier.

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

    def ping(self, channel="auth"):
        """Ping bitfinex."""
        client_cid = wss_utils.UtcNow()
        data = {
            'event': 'ping',
            'cid': client_cid
        }
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories[channel].protocol_instance.sendMessage(payload, isBinary=False)
        return client_cid

    def new_order_op(self, order_type, pair, amount, price, price_trailing=None,
                     price_aux_limit=None, price_oco_stop=None, hidden=0,
                     flags=None, tif=None):
        """
        Create new order operation

        Parameters
        ----------
        order_type : str
            Order type. Must be one of: "LIMIT", "STOP", "MARKET",
            "TRAILING STOP", "FOK", "STOP LIMIT" or equivelent with "MARKET"
            prepended to it.

        pair : str
            The currency pair to be traded. e.g. BTCUSD

        amount :  float
            The amount to be traided.

        price : float
            The price to buy at. Will be ignored for market orders.

        hidden : bool
            Whether or not to use the hidden order type.

        flags : list
            A list of integers for the different flags. Will be added together
            into a unique integer.

        Returns
        -------
        dict
            A dict containing the order detials. Used in new_order and for
            creating multiorders.
        """
        flags = flags or []
        client_order_id = wss_utils.UtcNow()
        order_op = {
            'cid': client_order_id,
            'type': order_type,
            'symbol': wss_utils.order_pair(pair),
            'amount': amount,
            'price': price,
            'hidden': hidden,
            "flags": sum(flags),
        }
        if price_trailing:
            order_op['price_trailing'] = price_trailing

        if price_aux_limit:
            order_op['price_aux_limit'] = price_aux_limit

        if price_oco_stop:
            order_op['price_oco_stop'] = price_oco_stop

        if tif:
            order_op['tif'] = tif

        return order_op

    def new_order(self, order_type, pair, amount, price, price_trailing=None,
                  price_aux_limit=None, price_oco_stop=None, hidden=0,
                  flags=None, tif=None):
        """
        Create new order.

        Parameters
        ----------
        order_type : str
            Order type. Must be one of: "LIMIT", "STOP", "MARKET",
            "TRAILING STOP", "FOK", "STOP LIMIT" or equivelent with "MARKET"
            prepended to it.

        pair : str
            The currency pair to be traded. e.g. BTCUSD

        amount :  decimal string
            The amount to be traided.

        price : decimal string
            The price to buy at. Will be ignored for market orders.

        price_trailing : decimal string
        	The trailing price

        price_aux_limit : decimal string
            Auxiliary Limit price (for STOP LIMIT)

        price_oco_stop : decimal string
            OCO stop price

        hidden : bool
            Whether or not to use the hidden order type.

        flags : list
            A list of integers for the different flags. Will be added together
            into a unique integer.

        tif : datetime string

        Returns
        -------
        int
            Order client id (cid). The CID is also a mts date stamp of when the
            order was created.
        """
        operation = self.new_order_op(
            order_type=order_type,
            pair=pair,
            amount=amount,
            price=price,
            price_trailing=price_trailing,
            price_aux_limit=price_aux_limit,
            price_oco_stop=price_oco_stop,
            hidden=hidden,
            flags=flags,
            tif=tif
        )
        data = [
            0,
            wss_utils.get_notification_code('order new'),
            None,
            operation
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)
        return operation["cid"]

    def multi_order(self, operations):
        """Multi order operation.

        Parameters
        ----------
        operations : list
            a list of operations. Read more here:
            https://bitfinex.readme.io/v2/reference#ws-input-order-multi-op
            Hint. you can use the self.new_order_op() for easy order
            operation creation.
        """
        data = [
            0,
            wss_utils.get_notification_code('order multi-op'),
            None,
            operations
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)
        return [order[1].get("cid", None) for order in operations]

    def cancel_order(self, order_id):
        """Cancel order

        Parameters
        ----------
        order_id : int, str
            Order id created by Bitfinex
        """
        data = [
            0,
            wss_utils.get_notification_code('order cancel'),
            None,
            {
                # docs: http://bit.ly/2BVqwW6
                'id': order_id
            }
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)

    def cancel_order_cid(self, order_cid, order_date):
        """Cancel order using the client id and the date of the cid. Both are
        returned from the new_order command from this library.

        Parameters
        ----------
        order_cid : str
            cid string. e.g. "1234154"

        order_date : str
            Iso formated order date. e.g. "2012-01-23"
        """
        data = [
            0,
            wss_utils.get_notification_code('order cancel'),
            None,
            {
                # docs: http://bit.ly/2BVqwW6
                'cid': order_cid,
                'cid_date': order_date
            }
        ]
        payload = json.dumps(data, ensure_ascii = False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)


    def update_order(self, **order_settings):
        """Update order using the order id

        Parameters
        ----------
        id : int64
            Order ID

        gid : int32
            Group Order ID

        price : decimal string
            Price

        amount : decimal string
            Amount

        delta : decimal string
            Change of amount

        price_aux_limit : decimal string
            Auxiliary limit price

        price_trailing : decimal string
            Trailing price delta

        tif : datetime string
            Time-In-Force: datetime for automatic order cancellation (ie. 2020-01-01 10:45:23)
        """
        data = [
            0,
            wss_utils.get_notification_code('order update'),
            None,
            order_settings
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)


    def calc(self, *calculations):
        """This message will be used by clients to trigger specific calculations,
                so we don't end up in calculating data that is not usually needed.
           You can request calculations to the websocket server that sends you the same message,
                with the required fields.
           Possible prefixes:
                margin_sym_SYMBOL (e.g. margin_sym_tBTCUSD)
                funding_sym_SYMBOL
                position_SYMBOL
                wallet_WALLET-TYPE_CURRENCY
           NOTE
                Calculations are on demand, so no more streaming of unnecessary data.
                Websocket server allows up to 30 calculations per batch.
                If the client sends too many concurrent requests (or tries to spam) requests,
                it will receive an error and potentially a disconnection.
                The Websocket server performs a maximum of 8 calculations per second per client.

            Parameters
            ----------
            *calculations : str
                margin_sym_SYMBOL
                funding_sym_SYMBOL
                position_SYMBOL
                wallet_WALLET-TYPE_CURRENCY
        """

        data = [
            0,
            'calc',
            None,
            calculations
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.factories["auth"].protocol_instance.sendMessage(payload, isBinary=False)
