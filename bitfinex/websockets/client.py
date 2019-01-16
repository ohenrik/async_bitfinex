# coding=utf-8
from datetime import datetime
import json
import hmac
import hashlib
import asyncio
import websockets

from bitfinex import utils
from . import abbreviations


STREAM_URL = 'wss://api.bitfinex.com/ws/2'

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

    ###########################################################################
    # Bitfinex commands
    ###########################################################################

    def __init__(self, key=None, secret=None, nonce_multiplier=1.0):  # client
        super().__init__()
        self.key = key
        self.secret = secret
        self.connections = {}
        self.nonce_multiplier = nonce_multiplier

    def _nonce(self):
        """Returns a nonce used in authentication.
        Nonce must be an increasing number, if the API key has been used
        earlier or other frameworks that have used higher numbers you might
        need to increase the nonce_multiplier."""
        return str(utils.get_nonce(self.nonce_multiplier))

    async def stop_channel(self, connection_name):
        """Closes one spesific webscoket connection by name

        Parameters
        ----------
        connection_name : str
            the name of the websocket connection to close.
        """
        print(f"Stopping: {connection_name}")
        await self.connections[connection_name].close()

    async def stop_all(self):
        """Closes all webscoket connections"""
        for connection_name in self.connections:
            await self.stop_channel(connection_name)

    async def create_connection(self, channel_name, payload, callback):
        """Create a new websocket connection, store the connection and
        assign a callback for incomming messages.

        Parameters
        ----------
        channel_name :  str
            Name/id of the websocket channel. Used when sending messages or for
            stopping a channel.

        payload : str
            A json dictionary containing the subscribe instructions for bitfinex.

        callback : func
            A function to use to handle incomming messages. This channel wil
            be handling all messages returned from operations like new_order or
            cancel_order, so make sure you handle all these messages.
        """
        async with websockets.connect(STREAM_URL) as websocket:
            await websocket.send(payload)
            self.connections[channel_name] = websocket
            async for message in self.connections[channel_name]:
                message = json.loads(message)
                if asyncio.iscoroutinefunction(callback):
                    await callback(message)
                else:
                    callback(message)

    async def authenticate(self, callback, filters=None):
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
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.create_connection("auth", payload, callback)
        return "auth"


    async def subscribe_to_ticker(self, symbol, callback):
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
        channel_name = "_".join(["ticker", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'ticker',
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.create_connection(channel_name, payload, callback)
        return channel_name

    async def subscribe_to_trades(self, symbol, callback):
        """Subscribe to the passed symbol trades data channel.

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
            my_client.subscribe_to_trades(
                symbol="BTCUSD",
                callback=my_handler
            )
            my_client.start()
        """
        symbol = utils.order_symbol(symbol)
        channel_name = "_".join(["trades", symbol])
        data = {
            'event': 'subscribe',
            'channel': 'trades',
            'symbol': symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.create_connection(channel_name, payload, callback)
        return channel_name

    # Precision: R0, P0, P1, P2, P3
    async def subscribe_to_orderbook(self, symbol, precision, length, callback):
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

        Example
        -------
         ::

            def my_handler(message):
                # Here you can do stuff with the messages
                print(message)

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)

            my_client.subscribe_to_orderbook(
                symbol="BTCUSD",
                precision="P1",
                callback=my_handler
            )
            my_client.start()
        """
        symbol = utils.order_symbol(symbol)
        channel_name = "_".join(["order", symbol])
        data = {
            "event": 'subscribe',
            "channel": "book",
            "prec": precision,
            "len": length,
            "symbol": symbol,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.create_connection(channel_name, payload, callback)
        return channel_name

    async def subscribe_to_candles(self, symbol, timeframe, callback):
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

        valid_tfs = ['1m', '5m', '15m', '30m', '1h', '3h', '6h', '12h', '1D',
                     '7D', '14D', '1M']
        if timeframe:
            if timeframe not in valid_tfs:
                raise ValueError("timeframe must be any of %s" % valid_tfs)
        else:
            timeframe = '1m'
        identifier = ('candles', symbol, timeframe)
        channel_name = "_".join(identifier)
        symbol = utils.order_symbol(symbol)
        key = 'trade:' + timeframe + ':' + symbol
        data = {
            'event': 'subscribe',
            'channel': 'candles',
            'key': key,
        }
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.create_connection(channel_name, payload, callback)
        return channel_name

    async def ping(self, channel="auth"):
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
        await self.connections[channel].send(payload)
        return client_cid

    def new_order_op(self, order_type, symbol, amount, price, price_trailing=None,
                     price_aux_limit=None, price_oco_stop=None, hidden=0,
                     flags=None, tif=None):
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
        flags = flags or []
        client_order_id = utils.create_cid()
        order_op = {
            'cid': client_order_id,
            'type': order_type,
            'symbol': utils.order_symbol(symbol),
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

    async def new_order(self, order_type, symbol, amount, price, price_trailing=None,
                  price_aux_limit=None, price_oco_stop=None, hidden=0,
                  flags=None, tif=None):
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
            my_client.start()

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
            price_trailing=price_trailing,
            price_aux_limit=price_aux_limit,
            price_oco_stop=price_oco_stop,
            hidden=hidden,
            flags=flags,
            tif=tif
        )
        data = [
            0,
            abbreviations.get_notification_code('order new'),
            None,
            operation
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.connections["auth"].send(payload)
        return operation["cid"]

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

    async def cancel_order(self, order_id):
        """Cancel order

        Parameters
        ----------
        order_id : int, str
            Order id created by Bitfinex

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

        """
        data = [
            0,
            abbreviations.get_notification_code('order cancel'),
            None,
            {
                # docs: http://bit.ly/2BVqwW6
                'id': order_id
            }
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.connections["auth"].send(payload)

    async def cancel_order_cid(self, order_cid, order_date):
        """Cancel order using the client id and the date of the cid. Both are
        returned from the new_order command from this library.

        Parameters
        ----------
        order_cid : str
            cid string. e.g. "1234154"

        order_date : str
            Iso formated order date. e.g. "2012-01-23"


        Example
        -------
         ::

            # You should only need to create and authenticate a client once.
            # Then simply reuse it later
            my_client = WssClient(key, secret)
            my_client.authenticate()
            my_client.start()

            # order_cid created by this library is always a milliseconds
            # time stamp. So you can just divide it by 1000 to get the timestamp.
            my_client.cancel_order(
                order_cid=1538911910035,
                order_date=(
                    datetime.utcfromtimestamp(
                        1538911910035/1000.0
                    ).strftime("%Y-%m-%d")
                )
            )

        """
        data = [
            0,
            abbreviations.get_notification_code('order cancel'),
            None,
            {
                # docs: http://bit.ly/2BVqwW6
                'cid': order_cid,
                'cid_date': order_date
            }
        ]
        payload = json.dumps(data, ensure_ascii=False).encode('utf8')
        await self.connections["auth"].send(payload)

    async def update_order(self, **order_settings):
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
        await self.connections["auth"].send(payload)

    async def calc(self, *calculations):
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
        await self.connections["auth"].send(payload)
