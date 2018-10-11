# Bitfinex Python Client

**Continuation of**: https://github.com/scottjbarr/bitfinex

A Python client for the Bitfinex API v1 and v2 + websockets for v2.

## Installation

    pip install bitfinex-v2

## Documentation

The full documentation is available here:
https://bitfinex.readthedocs.io/en/latest/

## Compatibility

This code has been tested on

- Python 3.6

At the moment the library is only supported from 3.6 and above.


## Contributing

Contributions are welcome and i will do my best to merge PR quickly.

Here are some guidelines that makes everything easier for everybody:

1. Fork it.
1. Create a feature branch containing only your fix or feature.
1. Preferably add/update tests. Features or fixes that don't have good tests
   won't be accepted before someone adds them (mostly...).
1. Create a pull request.

### Setup

Install the requirements:

    pip install -r requirements.txt

### Testing

This projects uses pytest, so to run all the tests use:

    pytest -v

At the moment functionality related to websocket v2 is not properly tested.

### TODO

- Add the remaining Websocket calls.
- Implement all API calls that Bitfinex make available (v1).

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
