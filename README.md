# Asyncio Python Client for Bitfinex

A Python client for the Bitfinex API v1 and v2 + websockets for v2.

## Installation

    pip install async_bitfinex

## Usage example


    from async_bitfinex import WssClient

    async def my_handler(message):
      """Function that react to incoming messages"""
      print(message)

    my_client = WssClient()
    my_client.subscribe_to_ticker(
        symbol="BTCUSD",
        callback=my_handler
    )

## Documentation

The full documentation is available here:
https://async_bitfinex.readthedocs.io/en/latest/

## Compatibility

This code has been tested on

- Python 3.7.1 and 3.7.2

At the moment the library is only supported from 3.7 and above.


# Contributing

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

- This project is originally base of: https://github.com/scottjbarr/bitfinex

## Licence

The MIT License (MIT)
