"""Websocket Client for Bitfinex V2 API."""
# coding=utf-8
import json
import hmac
import hashlib
import asyncio
import websockets
from websockets.protocol import State
from .. import utils
from . import abbreviations
from .futures_handler import FuturesHandler, CLIENT_HANDLERS

STREAM_URL = 'wss://api.bitfinex.com/ws/2'


class DummyState:
    state = State.CONNECTING

class TimedFuture(asyncio.Future):

    def __init__(self, timeout=None):
        super().__init__()
        if timeout:
            asyncio.ensure_future(self.trigger_timeout(timeout))

    async def trigger_timeout(self, timeout):
        await asyncio.sleep(timeout)
        if not self.done():
            self.set_exception(TimeoutError)


class WssClient():
    """Websocket client for bitfinex.

    Parameters
    ----------
    key : str
        Your API key.

    secret : str
        Your API secret


    .. Hint::

        Do not store your key or secret directly in the code.
        Use environment variables. and fetch them with
        ``os.environ.get("BITFINEX_KEY")``

    """

    def __init__(self, key=None, secret=None, nonce_multiplier=1.0, loop=None):  # client
        super().__init__()
        self.key = key
        self.secret = secret
        self.connections = {}
        self.nonce_multiplier = nonce_multiplier
        self.futures = FuturesHandler(CLIENT_HANDLERS)
        self.loop = loop or asyncio.get_event_loop()

    def stop(self):
        """Tries to close all connections and finally stops the reactor.
        Properly stops the program."""
        for connection in self.connections:
            connection.close()

    def _nonce(self):
        """Returns a nonce used in authentication.
        Nonce must be an increasing number, if the API key has been used
        earlier or other frameworks that have used higher numbers you might
        need to increase the nonce_multiplier."""
        return str(utils.get_nonce(self.nonce_multiplier))

    def close_connection(self, connection_name):
        """Closes one spesific webscoket connection by name

        Parameters
        ----------
        connection_name : str
            the name of the websocket connection to close.
        """
        print(f"Stopping: {connection_name}")
        self.connections[connection_name].close()

    def unsubscribe(self, connection_name, channel_id, timeout=None):
        if connection_name in self.connections:
            future_id = f"unsubscribe_{channel_id}"
            data = {
                "event": "unsubscribe",
                "chanId": channel_id
            }
            self.futures[future_id] = TimedFuture(timeout)
            self.futures[future_id].future_id = future_id
            payload = json.dumps(data, ensure_ascii=False).encode('utf8')
            asyncio.get_event_loop().create_task(
                self.connections[connection_name].send(payload)
            )
            return self.futures[future_id]

    async def create_connection(self, connection_name, payload, callback, **kwargs):
        """Create a new websocket connection, store the connection and
        assign a callback for incomming messages.

        Parameters
        ----------
        connection_name :  str
            Name/id of the websocket channel. Used when sending messages or for
            stopping a channel.

        payload : str
            A json dictionary containing the subscribe instructions for bitfinex.

        callback : func
            A function to use to handle incomming messages. This channel wil
            be handling all messages returned from operations like new_order or
            cancel_order, so make sure you handle all these messages.
        """
        empty_messages_callback = kwargs.get("empty_messages_callback", None)
        async with websockets.connect(STREAM_URL) as websocket:
            self.connections[connection_name] = websocket
            await websocket.send(payload)
            async for message in websocket:
                message = json.loads(message)
                self.futures(message)
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)
                if empty_messages_callback and (not websocket.messages):
                    if asyncio.iscoroutinefunction(empty_messages_callback):
                        await empty_messages_callback()
                    else:
                        empty_messages_callback()


    async def subscribe(self, connection_name, payload, create_connection=False,
                        callback=None, **kwargs):
        """Subscribes over existing connection if present. Creates new connection
        if needed."""
        if create_connection:
            # print("New connection created")
            assert callback, "Callback function cannot be None"
            asyncio.ensure_future(
                self.create_connection(connection_name, payload, callback,
                                       **kwargs)
            )
        else:
            while not self.connections[connection_name].state == State(1): #OPEN
                await asyncio.sleep(0.1)
            asyncio.get_event_loop().create_task(
                self.connections[connection_name].send(payload)
            )

    def authenticate(self, callback, filters=None, timeout=None, **kwargs):
        """Method used to create an authenticated channel that both recieves
        account spesific messages and is used to send account spesific messages.
        So in order to be able to use the new_order method, you have to
        create a authenticated channel before starting the connection.

        Parameters
        ----------
        callback : func
            A function to use to handle incomming messages. This channel wil
            be handling all messages returned from operations like new_order or
            cancel_order, so make sure you handle all these messages.

        filters : List[str]
            A list of filter strings. See more information here:
            https://docs.bitfinex.com/v2/docs/ws-auth#section-channel-filters

        Example
        -------
         ::

            def handle_account_messages(message):
                print(message)

             # You should only need to create and authenticate a client once.
             # Then simply reuse it later
             my_client = WssClient(key, secret)
             my_client.authenticate(
                callback=handle_account_messages
             )
             my_client.start()

        """
        nonce = self._nonce()
        auth_payload = 'AUTH{}'.format(nonce)
        signature = hmac.new(
            self.secret.encode(),  # settings.API_SECRET.encode()
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
        self.futures["auth"] = TimedFuture(timeout)
        self.futures["auth"].future_id = "auth"
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        asyncio.ensure_future(self.create_connection(
            connection_name="auth",
            payload=payload,
            callback=callback,
            **kwargs
        ))
        return self.futures["auth"]

    def subscribe_to_ticker(self, symbol, callback=None, timeout=None,
                            connection_name="ticker", **kwargs):
        """Subscribe to the passed symbol ticks data channel.

        Parameters
        ----------
        symbol : str
            Symbol to request data for.

        callback : func
            A function to use to handle incomming messages

        Example
        -------
         ::

            def my_handler(message):
                # Here you can do stuff with the messages
                print(message)

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate(print)
            my_client.subscribe_to_ticker(
                symbol="BTCUSD",
                callback=my_handler
            )
            my_client.start()
        """
        symbol = utils.order_symbol(symbol)
        future_id = "_".join(["ticker", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'ticker',
            'symbol': symbol,
        }
        self.futures[future_id] = TimedFuture(timeout)
        self.futures[future_id].future_id = future_id
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')

        create_connection = False
        if not self.connections.get(connection_name, False):
            self.connections[connection_name] = DummyState
            create_connection = True

        asyncio.get_event_loop().create_task(self.subscribe(
            connection_name=connection_name,
            payload=payload,
            callback=callback,
            create_connection=create_connection,
            **kwargs
        ))
        return self.futures[future_id]

    def subscribe_to_trades(self, symbol, callback=None, connection_name="trades",
                            timeout=None, **kwargs):
        """Subscribe to the passed symbol trades data channel.

        Parameters
        ----------
        symbol : str
            Symbol to request data for.

        callback : func
            A function to use to handle incomming messages

        timeout : int
            Seconds before subcribe request response future times out

        Returns
        -------
        str
            future id of subscribe request response


        Example
        -------
         ::

            def my_handler(message):
                # Here you can do stuff with the messages
                print(message)

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate(print)
            my_client.subscribe_to_trades(
                symbol="BTCUSD",
                callback=my_handler
            )
            my_client.start()
        """
        symbol = utils.order_symbol(symbol)
        future_id = "_".join(["trades", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'trades',
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.futures[future_id] = TimedFuture(timeout)
        self.futures[future_id].future_id = future_id
        create_connection = False
        if not self.connections.get(connection_name, False):
            self.connections[connection_name] = DummyState
            create_connection = True

        asyncio.get_event_loop().create_task(self.subscribe(
            connection_name=connection_name,
            payload=payload,
            callback=callback,
            create_connection=create_connection,
            **kwargs
        ))
        return self.futures[future_id]

    # Precision: R0, P0, P1, P2, P3
    def subscribe_to_orderbook(self, symbol, precision, length, callback=None,
                               connection_name="book", timeout=None, **kwargs):
        """Subscribe to the orderbook of a given symbol.

        Parameters
        ----------
        symbol : str
            Symbol to request data for.

        precision : str
            Accepted values as strings {R0, P0, P1, P2, P3}

        length : integer
            Accepted values are 25 and 100

        callback : func
            A function to use to handle incomming messages

        connection_name : str
            The connection handler string. Default: book

        Example
        -------
         ::

            def my_handler(message):
                # Here you can do stuff with the messages
                print(message)

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)

            my_client.connect_to_orderbook(
                symbol="BTCUSD",
                precision="P1",
                callback=my_handler
            )
        """
        symbol = utils.order_symbol(symbol)
        future_id = "_".join(["book", symbol])
        data = {
            "event": 'subscribe',
            "channel": "book",
            "prec": precision,
            "len": length,
            "symbol": symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.futures[future_id] = TimedFuture(timeout)
        self.futures[future_id].future_id = future_id

        create_connection = False
        if not self.connections.get(connection_name, False):
            self.connections[connection_name] = DummyState
            create_connection = True

        asyncio.get_event_loop().create_task(self.subscribe(
            connection_name=connection_name,
            payload=payload,
            callback=callback,
            create_connection=create_connection,
            **kwargs
        ))
        return self.futures[future_id]

    def subscribe_to_candles(self, symbol, timeframe, callback=None,
                             timeout=None, connection_name="candles", **kwargs):
        """Subscribe to the passed symbol's OHLC data channel.

        Parameters
        ----------
        symbol : str
            Symbol to request data for

        timeframe : str
            Accepted values as strings {1m, 5m, 15m, 30m, 1h, 3h, 6h, 12h,
            1D, 7D, 14D, 1M}

        callback : func
            A function to use to handle incomming messages

        Returns
        -------
        str
            The socket identifier.

        Example
        -------
         ::

            def my_candle_handler(message):
                # Here you can do stuff with the candle bar messages
                print(message)

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)

            my_client.subscribe_to_candles(
                symbol="BTCUSD",
                timeframe="1m",
                callback=my_candle_handler
            )
            my_client.subscribe_to_candles(
                symbol="ETHUSD",
                timeframe="5m",
                callback=my_candle_handler
            )
            my_client.start()

        """

        timeframe = timeframe or '1m'

        valid_tfs = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D',
                     '7D', '14D', '1M']

        if timeframe not in valid_tfs:
            raise ValueError("timeframe must be any of %s" % valid_tfs)

        symbol = utils.order_symbol(symbol)
        key = 'trade:' + timeframe + ':' + symbol
        identifier = ('candles', key)
        future_id = "_".join(identifier)
        data = {
            'event': 'subscribe',
            'channel': 'candles',
            'key': key,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.futures[future_id] = TimedFuture(timeout)
        self.futures[future_id].future_id = future_id
        create_connection = False
        if not self.connections.get(connection_name, False):
            self.connections[connection_name] = DummyState
            create_connection = True

        asyncio.get_event_loop().create_task(self.subscribe(
            connection_name=connection_name,
            payload=payload,
            callback=callback,
            create_connection=create_connection,
            **kwargs
        ))
        return self.futures[future_id]

    def ping(self, connection_name="auth", timeout=None):
        """Ping bitfinex.

        Parameters
        ----------
        channel : str
            What channel id that should be pinged. Default "auth".
            To get channel id’s use ´client._conns.keys()´.
        """
        client_cid = utils.create_cid()
        data = {
            'event': 'ping',
            'cid': client_cid
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        pong_future_id = f"pong_{client_cid}"
        self.futures[pong_future_id] = TimedFuture(timeout)
        self.futures[pong_future_id].future_id = pong_future_id
        asyncio.get_event_loop().create_task(self.connections[connection_name].send(payload))
        return self.futures[pong_future_id]

    @staticmethod
    def new_order_op(order_type, symbol, amount, price, **kwargs):
        """Create new order operation

        Parameters
        ----------
        order_type : str
            Order type. Must be one of: "LIMIT", "STOP", "MARKET",
            "TRAILING STOP", "FOK", "STOP LIMIT" or equivelent with "EXCHANGE"
            prepended to it. All orders starting with EXCHANGE are made on the
            exchange wallet. Orders without it is made on the margin wallet and
            will start or change a position.

        symbol : str
            The currency symbol to be traded. e.g. BTCUSD

        amount : decimal str
            The amount to be traided.

        price : decimal str
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

        set_cid : bool
            wheter or not to set a cid.

        Returns
        -------
        dict
            A dict containing the order detials. Used in new_order and for
            creating multiorders.

        Example
        -------
        Note if you only want to create a new order, use the ´´new_order´´
        method bellow. However if you want to submitt multiple order and
        cancel orders at the same time use this method to create order
        operations and send them with the ``multi_order`` method::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate()
            my_client.start()

            order_operation = my_client.new_order_op(
                order_type="LIMIT",
                symbol="BTCUSD",
                amount=0.004,
                price=1000.0
            )

            # Usefull to keep track of an order by its client id, for later
            # operations (like cancel order).
            clinet_id = order_operation["cid"]

            my_client.multi_order(
                operations=[order_operation]
            )

        """
        client_order_id = kwargs.get("cid", utils.create_cid())
        order_op = {
            'type': order_type,
            'symbol': utils.order_symbol(symbol),
            'amount': amount,
            'price': price,
            'hidden': kwargs.get("hidden", 0),
            "flags": sum(kwargs.get("flags", [])),
        }

        if kwargs.get("price_trailing"):
            order_op['price_trailing'] = kwargs.get("price_trailing")

        if kwargs.get("price_aux_limit"):
            order_op['price_aux_limit'] = kwargs.get("price_aux_limit")

        if kwargs.get("price_oco_stop"):
            order_op['price_oco_stop'] = kwargs.get("price_oco_stop")

        if kwargs.get("tif"):
            order_op['tif'] = kwargs.get("tif")

        client_order_id = utils.create_cid()
        order_op['cid'] = client_order_id

        return order_op

    def _create_new_order_future(self, cid, order_type, timeout=None):
        """Create future objects for new orders"""
        confirm_future_id = None
        if order_type in ("MARKET", "EXCHANGE MARKET"):
            confirm_future_id = f"oc_{cid}"
            self.futures[confirm_future_id] = TimedFuture(timeout)
        else:
            confirm_future_id = f"on_{cid}"
            self.futures[confirm_future_id] = TimedFuture(timeout)
        self.futures[confirm_future_id].future_id = confirm_future_id

        request_future_id = f"on-req_{cid}"
        self.futures[request_future_id] = TimedFuture(timeout)
        self.futures[request_future_id].future_id = request_future_id
        return (self.futures[request_future_id], self.futures[confirm_future_id])

    def new_order(self, order_type, symbol, amount, price, **kwargs):
        """
        Create new order.

        Parameters
        ----------
        order_type : str
            Order type. Must be one of: "LIMIT", "STOP", "MARKET",
            "TRAILING STOP", "FOK", "STOP LIMIT" or equivelent with "EXCHANGE"
            prepended to it. All orders starting with EXCHANGE are made on the
            exchange wallet. Orders without it is made on the margin wallet and
            will start or change a position.

        symbol : str
            The currency symbol to be traded. e.g. BTCUSD

        amount : decimal string
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

        timeout : int
            Seconds before future objects are timed out.

        Returns
        -------
        int
            Order client id (cid). The CID is also a mts date stamp of when the
            order was created.


        Example
        -------
         ::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate()


            order_client_id = my_client.new_order(
                order_type="LIMIT",
                symbol="BTCUSD",
                amount=0.004,
                price=1000.0
            )

        """
        operation = self.new_order_op(
            order_type=order_type,
            symbol=symbol,
            amount=amount,
            price=price,
            **kwargs
        )
        data = [
            0,
            abbreviations.get_notification_code('order new'),
            None,
            operation
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        # Create a future method for handling responses
        request_future, confirm_future = self._create_new_order_future(
            cid=operation["cid"],
            order_type=order_type,
            timeout=kwargs.get("timeout")
        )
        self.loop.create_task(self.connections["auth"].send(payload))
        return {
            "request_future": request_future,
            "confirm_future": confirm_future,
            "cid": operation['cid']
        }

    async def multi_order(self, operations):
        """Multi order operation.

        Parameters
        ----------
        operations : list
            a list of operations. Read more here:
            https://bitfinex.readme.io/v2/reference#ws-input-order-multi-op
            Hint. you can use the self.new_order_op() for easy new order
            operation creation.

        Returns
        -------
        list
            A list of all the client ids created for each order. Returned in
            the order they are given to the method.

        Example
        -------
         ::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            from bitfinex import utils
            my_client = WssClient(key, secret)
            my_client.authenticate()
            my_client.start()

            example_order_cid_to_cancel = 153925861909296

            # docs: http://bit.ly/2BVqwW6
            cancel_order_operation = {
                'cid': example_order_cid_to_cancel,
                'cid_date': utils.cid_to_date(example_order_cid_to_cancel)
            }

            new_order_operation = my_client.new_order_op(
                order_type="LIMIT",
                symbol="BTCUSD",
                amount=0.004,
                price=1000.0
            )

            order_client_id = my_client.multi_order([
                cancel_order_operation,
                new_order_operation
            ])
        """
        data = [
            0,
            abbreviations.get_notification_code('order multi-op'),
            None,
            operations
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.connections["auth"].send(payload)
        return [order[1].get("cid", None) for order in operations]

    def cancel_order(self, order_id=None, order_cid=None, order_date=None, timeout=None):
        """Cancel order using either the id (order_id) or the client id (order_cid).

        Parameters
        ----------
        order_id : int, str
            Order id created by Bitfinex
        order_cid : str
            cid string. e.g. "1234154"
        order_date : str
            Iso formated order date. e.g. "2012-01-23"
        timeout : int
            Seconds before future objects are timed out.

        Example
        -------
         ::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate()
            my_client.start()

            my_client.cancel_order(
                order_id=1234
            )

            # Using client id formated as timestamp * 10k (from utils)
            my_client.cancel_order(
                order_cid=1234
                # Optionally supply the order_date if you are using a custom cid format
                # order_date="2019-01-01"
            )

        """
        assert any([order_id, order_cid]), "Requires order_id or order_cid"

        if order_id:
            cancel_message = {'id': order_id}
        else:
            cancel_message = {
                # docs: http://bit.ly/2BVqwW6
                'cid': order_cid,
                'cid_date': order_date or utils.cid_to_date(order_cid)
            }

        data = [
            0,
            abbreviations.get_notification_code('order cancel'),
            None,
            cancel_message
        ]
        request_future_id = f"oc-req_{order_id or order_cid}"
        confirm_future_id = f"oc_{order_id or order_cid}"
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')

        self.futures[request_future_id] = TimedFuture(timeout)
        self.futures[request_future_id].future_id = request_future_id

        self.futures[confirm_future_id] = TimedFuture(timeout)
        self.futures[confirm_future_id].future_id = confirm_future_id

        self.loop.create_task(self.connections["auth"].send(payload))
        return {
            "request_future": self.futures[request_future_id],
            "confirm_future": self.futures[confirm_future_id],
            "id": order_id,
            "cid": order_cid,
            "cid_date": order_date
        }

    def update_order(self, timeout=None, **order_settings):
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
            abbreviations.get_notification_code('order update'),
            None,
            order_settings
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')

        request_future_id = f"ou-req_{order_settings['id']}"
        confirm_future_id = f"ou_{order_settings['id']}"
        self.futures[request_future_id] = TimedFuture(timeout)
        self.futures[request_future_id].future_id = request_future_id

        self.futures[confirm_future_id] = TimedFuture(timeout)
        self.futures[confirm_future_id].future_id = confirm_future_id

        self.loop.create_task(self.connections["auth"].send(payload))
        return {
            "request_future": self.futures[request_future_id],
            "confirm_future": self.futures[confirm_future_id],
            "id": order_settings['id']
        }

    def calc(self, *calculations):
        """
        This message will be used by clients to trigger specific calculations,
        so we don't end up in calculating data that is not usually needed.

        You can request calculations to the websocket server that sends you the
        same message, with the required fields.

        List items must be one of the following:

            - margin_sym_SYMBOL (e.g. margin_sym_tBTCUSD)
            - funding_sym_SYMBOL
            - position_SYMBOL
            - wallet_WALLET-TYPE_CURRENCY


        Parameters
        ----------
        *calculations : list
            list of calculations wanted

        Returns
        -------
        None
            Data is returned over the auth channel. See the abbreviation
            glossary: https://docs.bitfinex.com/v2/docs/abbreviations-glossary

        Examples
        --------
         ::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate(print)
            my_client.start()

            my_client.calc(["margin_sym_tBTCUSD", "funding_sym_fUSD"])
            my_client.calc(["margin_sym_tBTCUSD"])
            my_client.calc(["position_tBTCUSD"])
            my_client.calc(["wallet_exachange_USD"])

        .. Note::

            Calculations are on demand, so no more streaming of unnecessary data.
            Websocket server allows up to 30 calculations per batch.
            If the client sends too many concurrent requests (or tries to spam) requests,
            it will receive an error and potentially a disconnection.
            The Websocket server performs a maximum of 8 calculations per second per client.

        """

        data = [
            0,
            'calc',
            None,
            calculations
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        self.loop.create_task(self.connections["auth"].send(payload))
