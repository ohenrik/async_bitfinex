.. _websocket:

Websockets
==========

The code bellow is documented with complete examples of how to use the methods.

You should use a shared client object that is maintaned in your
application while it is running.

Quickstart example
------------------
 ::

    def my_candle_handler(message):
        # Here you can do stuff with the candle bar messages
        print(message)

    # You should only need to create and authenticate a client once.
    # Then simply reuse it later
    my_client = WssClient(key, secret)
    my_client.authenticate(print)
    
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

    # Wait a bit for the connection to go live
    import time
    time.sleep(5)

    # Then create a new order
    order_client_id = my_client.new_order(
        order_type="LIMIT",
        pair="BTCUSD",
        amount=0.004,
        price=1000.0
    )

WssClient - With Examples
---------

.. autoclass:: bitfinex.websockets.client.WssClient
    :members:
