# Bitfinex Python Client

**Continuation of**: https://github.com/scottjbarr/bitfinex

A Python client for the Bitfinex API.

Most of the unauthenticated calls have been implemented.  It is planned to
implement the remainder of the API.

## Installation

    pip install git+https://github.com/ohenrik/bitfinex



## Poll The Order Book

Run the ```bitfinex-poll-orderbook``` script in a terminal.

Press ```Ctrl-c``` to exit.

    bitfinex-poll-orderbook

## Setup

Install the libs

    pip install -r ./requirements.txt

## Usage REST API (v1)

    from bitfinex import Client
    client = Client(os.environ.get('BITFINEX_KEY'), os.environ.get('BITFINEX_SECRET'))

    self.client.ticker('btcusd')
    >>>>  { "mid": "562.56495",
            "bid": "562.15",
            "ask": "562.9799",
            "last_price": "562.25",
            "volume": "7842.11542563",
            "timestamp": "1395552658.339936691"
          }

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


So far only the auth channel and candle stick channel is implemented.

For sending messages I have only implemented new_order and cancel_order.
I will add documentation for this later, for now take a look at the source code.

## Compatibility

This code has been tested on

- Python 3.6.3

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

- Implement all API calls that Bitfinex make available (v1).
- Add v2 REST api logic
- Add the rest of Websocket messages and channels.

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
