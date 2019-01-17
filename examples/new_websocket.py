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

    request_response = await client.futures[handles["req_id"]]
    print("Request response received")
    print(request_response)

    confirmation_response = await client.futures[handles["confirm_id"]]
    print("Confirmation response received")
    print(confirmation_response)

    return request_response

async def cancel_order(client, cid):
    await asyncio.sleep(3)
    handles = client.cancel_order(
        # id=_id # Can use either id, or cid (+cid_date)
        order_cid=cid
    )
    cancel_req_response = await client.futures[handles["req_id"]]
    print("Cancel Request response Received")
    print(cancel_req_response)

    cancel_conirm = await client.futures[handles["confirm_id"]]
    print("Cancel Confirm response Received")
    print(cancel_conirm)
    # If an order is not active it will not thow an error with any id or cid.
    # This means that the best/only way to pick up errors is to
    # timeout the future object. Se example bellow
    #     await asyncio.wait_for(
    #         client.futures[handles["req_id"]],
    #         timeout=self.timeout_seconds
    #     )

async def main():
    client = WssClient(
        key=os.environ.get("BITFINEX_KEY"),
        secret=os.environ.get("BITFINEX_SECRET")
    )
    asyncio.ensure_future(client.authenticate(print))
    # asyncio.ensure_future(client.subscribe_to_trades(symbol="BTCUSD", callback=async_print))
    order_response = await create_order(client)
    # pylint: disable=W0612
    await cancel_order(client, order_response["cid"])


if __name__ == '__main__':
    main_loop = asyncio.get_event_loop()
    asyncio.ensure_future(main())
    main_loop.run_forever()
