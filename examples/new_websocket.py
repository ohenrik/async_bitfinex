import os
import asyncio
from bitfinex import WssClient

async def async_print(message):
    """Helper just to print messages async"""
    print(message)

def main():
    client = WssClient(
        key=os.environ.get("BITFINEX_KEY"),
        secret=os.environ.get("BITFINEX_SECRET")
    )
    subscriptions = asyncio.wait([
        client.subscribe_to_trades(symbol="BTCUSD", callback=async_print),
        client.authenticate(async_print),
    ])
    asyncio.run(subscriptions)

if __name__ == '__main__':
    main()
