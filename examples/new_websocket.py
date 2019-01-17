import os
import asyncio
from bitfinex import WssClient

async def async_print(message):
    """Helper just to print messages async"""
    print(message)

async def create_order(client):
    await asyncio.sleep(3)
    message = await client.new_order(
        order_type="LIMIT",
        symbol="BTCUSD",
        amount="0.008",
        price="1000.0"
    )
    print("message_received")
    print(message)
    return message

async def cancel_order(client, cid):
    await asyncio.sleep(3)
    cancel_message = await client.cancel_order(
        # id=_id # Can use either id, or cid (+cid_date)
        order_cid=cid
    )
    print("cancel message_received")
    print(cancel_message)
    return cancel_message

async def continue_to_listen():
    while True:
        await asyncio.sleep(0.1)

async def main():
    client = WssClient(
        key=os.environ.get("BITFINEX_KEY"),
        secret=os.environ.get("BITFINEX_SECRET")
    )
    asyncio.ensure_future(client.authenticate(async_print))
    asyncio.ensure_future(client.subscribe_to_trades(symbol="BTCUSD", callback=async_print))
    order_response = await create_order(client)
    # pylint: disable=W0612
    cancel_order_response = await cancel_order(client, order_response["cid"])
    await asyncio.sleep(3)

    # Continue to listen for answers after cancel order completed.
    # await continue_to_listen()

if __name__ == '__main__':
    asyncio.run(main())
