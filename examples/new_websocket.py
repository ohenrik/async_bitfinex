import os
import asyncio
from bitfinex import WssClient

async def create_order(client):
    await asyncio.sleep(3)
    handles = client.new_order(
        order_type="LIMIT",
        symbol="BTCUSD",
        amount="0.008",
        price="1000.0",
        # hidden=1
    )

    request_response = await handles["request_future"]
    print("Request response received")
    print(request_response)

    confirmation_response = await handles["confirm_future"]
    print("Confirmation response received")
    print(confirmation_response)

    return confirmation_response

async def update_order(client, id, price, amount):
    await asyncio.sleep(3)
    handles = client.update_order(
        # id=_id # Can use either id, or cid (+cid_date)
        id=id,
        price=price,
        amount=amount,
        timeout=10
    )
    try:
        request_response = await handles["request_future"]
        print("Update Request response Received")
        print(request_response)

        confirm_response = await handles["confirm_future"]
        print("Update Confirm response Received")
        print(confirm_response)
    except TimeoutError:
        # If an order is not active it will not thow an error with any id or cid.
        # This means that the best/only way to pick up errors is to
        # catch a TimeoutError
        print("Update Order timed out.")

async def cancel_order(client, cid):
    await asyncio.sleep(3)
    handles = client.cancel_order(
        # id=_id # Can use either id, or cid (+cid_date)
        order_cid=cid,
        timeout=10
    )
    try:
        cancel_req_response = await handles["request_future"]
        print("Cancel Request response Received")
        print(cancel_req_response)

        cancel_confirm = await handles["confirm_future"]
        print("Cancel Confirm response Received")
        print(cancel_confirm)
    except TimeoutError:
        # If an order is not active it will not thow an error with any id or cid.
        # This means that the best/only way to pick up errors is to
        # catch a TimeoutError
        print(
            "Cancel Order timed out. This can happen if the order was "
            "already canceled, excuted or never existed."
        )

async def main():
    client = WssClient(
        key=os.environ.get("BITFINEX_KEY"),
        secret=os.environ.get("BITFINEX_SECRET")
    )
    auth_future = client.authenticate(print, timeout=3)
    print(auth_future.future_id)
    print(await auth_future)

    trades_future = client.subscribe_to_trades(symbol="BTCUSD", callback=print, timeout=3)
    print(await trades_future)

    # book_future = client.subscribe_to_orderbook(symbol="BTCUSD", precision="P0", length=25, callback=lambda x: x)
    # print(await book_future)

    # tick_future = client.subscribe_to_ticker(symbol="BTCUSD", callback=lambda x: x)
    # print(await tick_future)

    # candle_future_ = client.subscribe_to_candles(symbol="BTCUSD", timeframe="1m", callback=lambda x: x)
    # print(await candle_future)

    # order_response = await create_order(client)
    # # pylint: disable=W0612
    # update_response = await update_order(client, id=order_response["id"], price="1010.0", amount="0.1")
    # print(update_response, order_response)
    # await cancel_order(client, order_response["cid"])



if __name__ == '__main__':
    main_loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    main_loop.run_forever()
