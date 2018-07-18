#!/usr/bin/python
#-*- coding: utf-8 -*-

from __future__ import absolute_import
import requests
import json
from json.decoder import JSONDecodeError
import hmac
import hashlib
import time


PROTOCOL = "https"
HOST = "api.bitfinex.com"
VERSION = "v2"


# HTTP request timeout in seconds
TIMEOUT = 5.0


class BitfinexException(Exception):
    pass


class Client:
    """
    Client for the bitfinex.com API REST V2.

    See https://bitfinex.readme.io/v2/docs and https://bitfinex.readme.io/v2/reference for documentation.
    """

    def __init__(self, key=None, secret=None, nonce_multiplier=1.0):
        assert type(nonce_multiplier) == float, "nonce_multiplier must be decimal"
        self.BASE_URL = "%s://%s/" % (PROTOCOL, HOST)
        self.KEY = key
        self.SECRET = secret
        self.nonce_multiplier = nonce_multiplier

    def _nonce(self):
        """Returns a nonce used in authentication.
        Nonce must be an increasing number, if the API key has been used
        earlier or other frameworks that have used higher numbers you might
        need to increase the nonce_multiplier."""
        return str(float(time.time()) * self.nonce_multiplier)

    def _headers(self, path, nonce, body):
        signature = "/api/" + path + nonce + body
        h = hmac.new(self.SECRET.encode('utf8'), signature.encode('utf8'), hashlib.sha384)
        signature = h.hexdigest()

        return {
            "bfx-nonce": nonce,
            "bfx-apikey": self.KEY,
            "bfx-signature": signature,
            "content-type": "application/json"
        }

    def _post(self, path, payload, verify=False):
        nonce    = self._nonce()
        headers  = self._headers(path, nonce, payload)
        response = requests.post(self.BASE_URL + path, headers=headers, data=payload, verify=True)

        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text()
            raise BitfinexException(response.status_code, response.reason, content)



    def _get(self, url,**params):
        response = requests.get(url, timeout=TIMEOUT,params=params)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text()
            raise BitfinexException(response.status_code, response.reason, content)




    # REST PUBLIC ENDPOINTS
    def platform_status(self):
        """
        Get the current status of the platform. Maintenance periods last for just few minutes
        and might be necessary from time to time during upgrades of core components of our infrastructure.
        Even if rare it is important to have a way to notify users. For a real-time notification
        we suggest to use websockets and listen to events 20060/20061
        https://bitfinex.readme.io/v2/reference#rest-public-platform-status

        Response details : 	int	1=operative, 0=maintenance
        """
        url = self.BASE_URL + "v2/platform/status"
        response = self._get(url)
        return response



    def tickers(self,symbol_list):
        """
        The ticker is a high level overview of the state of the market.
        It shows you the current best bid and ask, as well as the last trade price.
        It also includes information such as daily volume and how much the price has moved over the last day.
        https://bitfinex.readme.io/v2/reference#rest-public-tickers

        """
        assert type(symbol_list) == list, "symbol_list must be of type list"
        assert len(symbol_list) > 0, "symbol_list must have at least one symbol"
        url = self.BASE_URL + "v2/tickers?symbols="+symbol_list[0]
        for index in range(1,len(symbol_list)):
            url += ","+str(symbol_list[index])
        response = self._get(url)
        return response

    def ticker(self,symbol):
        """
        The ticker is a high level overview of the state of the market.
        It shows you the current best bid and ask, as well as the last trade price.
        It also includes information such as daily volume and how much the price has moved over the last day.
        https://bitfinex.readme.io/v2/reference#rest-public-ticker
        """
        url = self.BASE_URL + "v2/ticker/"+str(symbol)
        response = self._get(url)
        return response



    def trades(self,symbol):
        """
        Trades endpoint includes all the pertinent details of the trade, such as price, size and time.
        https://bitfinex.readme.io/v2/reference#rest-public-trades
        """
        url = self.BASE_URL + "v2/trades/"+symbol+"/hist"
        response = self._get(url)
        return response


    def books(self,symbol,precision="P0"):
        """
        The Order Books channel allow you to keep track of the state of the Bitfinex order book.
        It is provided on a price aggregated basis, with customizable precision.
        https://bitfinex.readme.io/v2/reference#rest-public-books
        Params : 
            symbol : The symbol you want information about. You can find the list of valid symbols by calling the /symbols endpoint.
            precision : Level of price aggregation (P0, P1, P2, P3, R0)
        """
        url = self.BASE_URL + "v2/book/"+symbol+"/"+precision
        response = self._get(url)
        return response


    def stats(self,**kwargs):
        """
        Various statistics about the requested pair.
        https://bitfinex.readme.io/v2/reference#rest-public-stats
        Params : 
            Key     : Allowed values: "funding.size", "credits.size", "credits.size.sym", "pos.size"
            Size    : Available values: '1m'
            Symbol  : The symbol you want information about.
            Symbol2 : The symbol you want information about.
            Side    : Available values: "long", "short"
            Section : Available values: "last", "hist"  
            sort    : 0 , 1
        """
        if kwargs['key'] not in ['funding.size', 'credits.size', 'credits.size.sym', 'pos.size']:
            raise ValueError("Key must have one of the following values : 'funding.size', 'credits.size', 'credits.size.sym', 'pos.size' ")
        
        if kwargs['key'] == 'pos.size':
            url = self.BASE_URL + "v2/stats1/"+kwargs['key']+":"+kwargs['size']+":"+kwargs['symbol']+":"+kwargs['side']+"/"+kwargs['section']+"?sort="+str(kwargs['sort'])

        if kwargs['key'] in ['funding.size','credits.size']:
            url = self.BASE_URL + "v2/stats1/"+kwargs['key']+":"+kwargs['size']+":"+kwargs['symbol']+"/"+kwargs['section']+"?sort="+str(kwargs['sort'])

        if kwargs['key'] == 'credits.size.sym':
            url = self.BASE_URL + "v2/stats1/"+kwargs['key']+":"+kwargs['size']+":"+kwargs['symbol']+":"+kwargs['symbol2']+"/"+kwargs['section']+"?sort="+str(kwargs['sort'])

        response = self._get(url)
        return response

    def candles(self,*args,**kwargs):
        """
        Provides a way to access charting candle info
        https://bitfinex.readme.io/v2/reference#rest-public-candles
        """
        margs = list(args)
        section = margs.pop()
        url = self.BASE_URL + "v2/candles/trade"
        for arg in margs:
            url = url + ":" + arg
        url += "/"+section
        response = self._get(url,**kwargs)
        return response



    #REST CALCULATION ENDPOINTS
    def market_average_price(self,**kwargs):
        """
        Calculate the average execution rate for Trading or Margin funding.
        https://bitfinex.readme.io/v2/reference#rest-calc-market-average-price
        """
        body = kwargs
        rawBody = json.dumps(body)
        path = "v2/calc/trade/avg"
        response = self._post(path,rawBody,verify=True)
        return response


    def foreign_exchange_rate(self,**kwargs):
        """
        https://bitfinex.readme.io/v2/reference#foreign-exchange-rate
        """
        body = kwargs
        rawBody = json.dumps(body)
        path = "v2/calc/fx"
        response = self._post(path,rawBody,verify=True)
        return response




    #REST AUTHENTICATED ENDPOINTS
    def wallets_balance(self):
        """
        Get account wallets
        https://bitfinex.readme.io/v2/reference#rest-auth-wallets
        """

        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/wallets"
        response = self._post(path,rawBody,verify=True)
        return response



    def active_orders(self,trade_pair=""):
        """
        Fetch active orders using rest api v2
        https://bitfinex.readme.io/v2/reference#rest-auth-orders
        """

        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/orders/"+trade_pair
        response = self._post(path,rawBody,verify=True)
        return response


    def orders_history(self,trade_pair):
        """
        Returns the most recent closed or canceled orders up to circa two weeks ago
        https://bitfinex.readme.io/v2/reference#orders-history
        """

        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/orders/"+trade_pair+"hist"
        response = self._post(path,rawBody,verify=True)
        return response

    def order_trades(self,trade_pair,order_id):
        """
        Get Trades generated by an Order
        https://bitfinex.readme.io/v2/reference#rest-auth-order-trades
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/order/"+trade_pair+":"+str(order_id)+"/trades"
        response = self._post(path,rawBody,verify=True)
        return response


    def trades_history(self,trade_pair):
        """
        Returns list of trades
        https://api.bitfinex.com/v:version/auth/r/trades/:Symbol/hist
        """

        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/trades/"+trade_pair+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def active_positions(self):
        """
        Returns list of active Positions
        https://bitfinex.readme.io/v2/reference#rest-auth-positions
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/positions"
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_offers(self,symbol=""):
        """
        Get active funding offers.
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-offers
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/offers/"+symbol
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_offers_history(self,symbol=""):
        """
        Get past inactive funding offers. Limited to last 3 days.
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-offers-hist
        """
        body = {}
        rawBody = json.dumps(body)
        addsymbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/offers/"+addsymbol+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_loans(self,symbol=""):
        """
        Funds not used in active positions
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-loans
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/loans/"+symbol
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_loans_history(self,symbol=""):
        """
        Inactive funds not used in positions. Limited to last 3 days.
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-loans-hist
        """
        body = {}
        rawBody = json.dumps(body)
        addsymbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/loans/"+addsymbol+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_credits(self,symbol=""):
        """
        Funds used in active positions
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-credits
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/funding/credits/"+symbol
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_credits_history(self,symbol=""):
        """
        Inactive funds used in positions. Limited to last 3 days.
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-credits-hist
        """
        body = {}
        rawBody = json.dumps(body)
        addsymbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/credits/"+addsymbol+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_trades(self,symbol=""):
        """
        Get funding trades
        https://bitfinex.readme.io/v2/reference#rest-auth-funding-trades-hist
        """
        body = {}
        rawBody = json.dumps(body)
        addsymbol = "{}/".format(symbol) if symbol else ""
        path = "v2/auth/r/funding/trades/"+addsymbol+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def margin_info(self,tradepair="base"):
        """
        Get account margin info
        https://bitfinex.readme.io/v2/reference#rest-auth-info-margin
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/info/margin/"+tradepair
        response = self._post(path,rawBody,verify=True)
        return response


    def funding_info(self,tradepair):
        """
        Get account funding info
        https://bitfinex.readme.io/v2/reference#rest-auth-info-funding
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/info/funding/"+tradepair
        response = self._post(path,rawBody,verify=True)
        return response


    def movements(self,currency=""):
        """
        View your past deposits/withdrawals.
        https://bitfinex.readme.io/v2/reference#movements
        """
        body = {}
        rawBody = json.dumps(body)
        addcurrency = "{}/".format(currency.upper()) if currency else ""
        path = "v2/auth/r/movements/"+addcurrency+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def performance(self,period="1D"):
        """
        Get account historical daily performance (work in progress on Bitfinex side)
        Work in progress
        This endpoint is still under active development so you might experience unexpected behavior from it.
        https://bitfinex.readme.io/v2/reference#rest-auth-performance

        Currently not working : bitfinex.rest.restv2.BitfinexException: (500, 'Internal Server Error', ['error', 10020, 'method: invalid'])
        """
        body = {}
        rawBody = json.dumps(body)
        path = "v2/auth/r/stats/perf:"+period+"/hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def alert_list(self):
        """
        List of active alerts
        https://api.bitfinex.com/v:version/auth/r/alerts
        """
        body = {'type':'price'}
        rawBody = json.dumps(body)
        path = "v2/auth/r/alerts"
        response = self._post(path,rawBody,verify=True)
        return response

    """
        nonce    = self._nonce()
        url=self.BASE_URL + path
        payload = rawBody
        headers  = self._headers(path, nonce, payload)
        payload = {'type': 'price'}
        response = requests.get(url, params=payload, timeout=TIMEOUT, headers=headers)
        print(response.url)
        print(response.headers)
        if response.status_code == 200:
            return response.json()
        else:
            try:
                content = response.json()
            except JSONDecodeError:
                content = response.text()
            raise BitfinexException(response.status_code, response.reason, content)
    """


    def alert_set(self,alert_type,symbol,price):
        """
        Sets up a price alert at the given value
        https://bitfinex.readme.io/v2/reference#rest-auth-alert-set
        """
        body = {
            'type'   : alert_type,
            'symbol' : symbol,
            'price'  : price
        }

        rawBody = json.dumps(body)
        path = "v2/auth/w/alert/set"
        response = self._post(path,rawBody,verify=True)
        return response


    def alert_delete(self,symbol,price):
        """
        https://bitfinex.readme.io/v2/reference#rest-auth-alert-delete
        Bitfinex always returns [True] no matter if the request deleted an alert or not
        """
        body = {}

        rawBody = json.dumps(body)
        path = "v2/auth/w/alert/price:"+symbol+":"+str(price)+"/del"
        response = self._post(path,rawBody,verify=True)
        return response


    def calc_available_balance(self,symbol,direction,rate,order_type):
        """
        Calculate available balance for order/offer
        https://bitfinex.readme.io/v2/reference#rest-auth-calc-bal-avail
        example : calc_available_balance("tIOTUSD","1","1.13","EXCHANGE")
        QUERY PARAMS : 
            symbol : symbol (string)
            dir    : direction of the order/offer (orders: > 0 buy, < 0 sell | offers: > 0 sell, < 0 buy) (integer)
            rate   : Rate of the order/offer (string)
            type   : Type of the order/offer EXCHANGE or MARGIN (string)
        """

        body = {
            'symbol' : symbol,
            'dir'    : direction,
            'rate'   : rate,
            'type'   : order_type
        }

        rawBody = json.dumps(body)
        path = "v2/auth/calc/order/avail"
        response = self._post(path,rawBody,verify=True)
        return response


    def ledgers(self,currency=""):
        """
        View your past ledger entries.
        https://bitfinex.readme.io/v2/reference#ledgers
        """
        body = {}
        rawBody = json.dumps(body)
        addcurrency = "{}/".format(currency.upper()) if currency else ""
        path = "v2/auth/r/ledgers/"+addcurrency+"hist"
        response = self._post(path,rawBody,verify=True)
        return response


    def user_settings_read(self,pkey):
        """
        Read user settings
        https://bitfinex.readme.io/v2/reference#user-settings-read
        """
        body = { 'keys': [ 'api:'+str(pkey) ] }
        rawBody = json.dumps(body)
        path = "v2/auth/r/settings"
        response = self._post(path,rawBody,verify=True)
        return response


    def user_settings_write(self,pkey):
       pass


    def user_settings_delete(self,pkey):
       pass



