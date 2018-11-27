#!/usr/bin/env python3
import os
import threading
import logging
from time import sleep
from bitfinex.websockets.client import WssClient

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.DEBUG
)
LOGGER = logging.getLogger(__name__)


KEY = os.environ.get("API_KEY")
SECRET = os.environ.get("API_SECRET")


class MyWssTest():

    def __init__(self):
        self.mywss = WssClient(key=KEY, secret=SECRET)
        self.mywss2 = None
        # Tracks Websocket Connection
        self.connection_timer = None
        self.connection_timeout = 15
        self.keep_running = True
        self.wssactions = {
            'hb': self._heartbeat_handler
        }
        self.mywss.authenticate(self.cb_auth)
        self.mywss.start()
        sleep(5)
        self._start_timers()

    def cb_auth(self, message):
        LOGGER.info(f"cb_auth received {message}")
        if isinstance(message, list):
            msg_type = message[1]
            if msg_type in self.wssactions:
                self.wssactions[msg_type]()

    def _stop_timers(self):
        """Stops connection timers."""
        if self.connection_timer:
            self.connection_timer.cancel()
        LOGGER.info("_stop_timers(): Timers stopped.")

    def _start_timers(self):
        """Resets and starts timers for API data and connection."""
        LOGGER.info("_start_timers(): Resetting timers..")
        self._stop_timers()
        # Automatically reconnect if we didnt receive data
        self.connection_timer = threading.Timer(self.connection_timeout, self._connection_timed_out)
        self.connection_timer.start()

    def _connection_timed_out(self):
        """Issues a reconnection if the connection timed out.
        :return:
        """
        LOGGER.info("_connection_timed_out(): Fired! Issuing reconnect..")
        self.mywss.authenticate(self.cb_auth)

    def _heartbeat_handler(self):
        LOGGER.info("new hb received")
        LOGGER.info(f"nonce is {self.mywss._nonce()}")
        self._start_timers()

    def run(self):
        counter = 0
        while self.keep_running:
            sleep(1)
            counter += 1
            infomsg = (f'#run nr : {counter} || '
                       f'thread alive : {self.mywss.is_alive()} || '
                       f'nr of active  threads : {threading.active_count()}')
            print(infomsg)

            # example new order
            # if counter == 5:
            #     exch_order = self.mywss.new_order("EXCHANGE LIMIT", "tIOTUSD", "-1000", "30")
            #     print(f"new order is {exch_order}")

            # example update order
            # if counter == 7:
            #     update_info = {
            #         "id": "16666882406",
            #         "delta": "-400"
            #     }
            #     self.mywss.update_order(**update_info)

            # example use calculations
            if counter == 8:
                self.mywss.calc(["position_tIOTUSD"])

            # first reconnect test
            if counter == 20:
                self.stopit()

            # second reconnect test
            if counter == 50:
                self.stopit()

    def stopit(self):
        LOGGER.info("trying to stop")
        self.mywss.close()


print("###############START##############")
MYOBJ = MyWssTest()
print("###############END##############")

MYOBJ.run()
