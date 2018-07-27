# Bitfinex Python Client

**Continuation of**: https://github.com/scottjbarr/bitfinex

A Python client for the Bitfinex API v1 and v2 + websockets for v2.

## Installation

    pip install bitfinex-v2

## Setup

Install the libs

    pip install -r ./requirements.txt

## Documentation

Full documentation coming soon. Please refer to the code to see function
names etc. for now.


## Usage REST API (v2)

    from bitfinex import ClientV2 as Client
    client = Client(
        os.environ.get('BITFINEX_KEY'),
        os.environ.get('BITFINEX_SECRET')
    )

    client.ticker('tBTCUSD')
    >>>>  [0.00011989,
          224267.1563644,
          0.00012015,
          265388.46405117,
          -8.12e-06,
          -0.0634,
          0.00012,
          3206446.72556849,
          0.00012812,
          0.00011545
    ]

## Usage Websockets API (v2)

The documentation for bitfinex websockets are somewhat confusing
So expect to spend some time figuring out just what is actually returned
through the authenticated channel.

    import os
    key = os.environ.get("API_KEY")
    secret = os.environ.get("API_SECRET")
    from bitfinex.websockets import WssClient
    bm = WssClient(key, secret)

    # Authenticate and listen to account feedback
    # print is the callback method. You probably want to do something else.
    bm.authenticate(print)

    # Subscribe to candles (starts with a set of completed candles, then updates with last completed + updated uncompleted candle)
    bm.subscribe_to_candles("BTCUSD", "1m", print)
    bm.start()

    # Send new order
    bm.new_order(order_type="EXCHANGE LIMIT", pair="BTCUSD", amount="0.1", price="1", hidden=0)

For sending messages I have only implemented new_order and cancel_order.
I will add documentation for this later, for now take a look at the source code.


## Usage REST API (v1)

    from bitfinex import ClientV1 as Client
    client = Client(
      os.environ.get('BITFINEX_KEY'),
      os.environ.get('BITFINEX_SECRET')
    )

    client.ticker('btcusd')
    >>>>  { "mid": "562.56495",
            "bid": "562.15",
            "ask": "562.9799",
            "last_price": "562.25",
            "volume": "7842.11542563",
            "timestamp": "1395552658.339936691"
          }


## Compatibility

This code has been tested on

- Python 3.6

But the REST library will probably work on python 2.7 as well.

I haven’t tested the Websocket library on 2.7

## Tests

When continuing this project (from scottjbarr) I decided to use pytests.

so this should start your tests:

    pytest -v

However... Due to the fact that Mocket (python-mocket) crashes whenever
pyopenssl is installed. Tests related to the rest library does now work unless
you uninstall pyopenssl.

## TODO

- Add the rest of Websocket messages and channels.
- Possible parsing improvement for v2 responses.
- Implement all API calls that Bitfinex make available (v1).

## Contributing

Contributions are welcome and i will do my best to merge PR quickly.

Here are some guidelines that makes everything easier for everybody:

1. Fork it.
1. Create a feature branch containing only your fix or feature.
1. Preferably add/update tests. Features or fixes that don't have good tests won't be accepted before someone adds them (mostly...).
1. Create a pull request.


## References

- This project is a continuation of: https://github.com/scottjbarr/bitfinex
- [https://www.bitfinex.com/pages/api](https://www.bitfinex.com/pages/api)
- [https://community.bitfinex.com/showwiki.php?title=Sample+API+Code](https://community.bitfinex.com/showwiki.php?title=Sample+API+Code)
- [https://gist.github.com/jordanbaucke/5812039](https://gist.github.com/jordanbaucke/5812039)

## Licence

The MIT License (MIT)

Copyright (c) 2014-2015 Scott Barr
^ Original project created by this guy.

See [LICENSE.md](LICENSE.md)
