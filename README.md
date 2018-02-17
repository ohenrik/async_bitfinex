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

## Usage

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


## Compatibility

This code has been tested on

- Python 3.6.3

But will probably work on python 2.7 as well.

## Tests

Depending on your system, install one of the following libs

- pyinotify (Linux)
- pywin32 (Windows)
- MacFSEvents (OSX)

Sniffer will watch for changes

    sniffer -x --nocapture

Or Sniffer with code coverage enabled...

    sniffer -x --nocapture -x--with-coverage -x--cover-html -x--cover-package=bitfinex

Or you can just run the tests

    nosetests

### Test Coverage

Test coverage of the code. View cover/index.html to view detailed reports.

    nosetests --with-coverage --cover-html --cover-package bitfinex


## TODO

- Implement all API calls that Bitfinex make available.

## Contributing

1. Create an issue and discuss.
1. Fork it.
1. Create a feature branch containing only your fix or feature.
1. Add tests!!!! Features or fixes that don't have good tests won't be accepted.
1. Create a pull request.

## References

- [https://www.bitfinex.com/pages/api](https://www.bitfinex.com/pages/api)
- [https://community.bitfinex.com/showwiki.php?title=Sample+API+Code](https://community.bitfinex.com/showwiki.php?title=Sample+API+Code)
- [https://gist.github.com/jordanbaucke/5812039](https://gist.github.com/jordanbaucke/5812039)

## Licence

The MIT License (MIT)

Copyright (c) 2014-2015 Scott Barr

See [LICENSE.md](LICENSE.md)
