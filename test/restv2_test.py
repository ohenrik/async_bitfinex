import unittest
import json
import requests
from mock import patch, Mock

from bitfinex.rest.restv2 import Client

class BitfinexTest(unittest.TestCase):

    def setUp(self):
        self.client = Client()

    def test_instantiate_client(self):
        """test instantiate client"""
        self.assertIsInstance(self.client, Client)

    @patch.object(requests, 'post')
    def testm1_platform_status(self, mockpost):
        """test method 1/34 platform_status"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = '[1]'
        platform_status = self.client.platform_status()
        self.assertEqual([1], platform_status)

    @patch.object(requests, 'post')
    def testm2_shoud_have_tickers(self, mockpost):
        """test method 2/34 tickers"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            ['tIOTBTC',
             0.00012012,
             207246.56609548,
             0.00012048,
             230371.29034138,
             -8.28e-06,
             -0.0644,
             0.00012035,
             3215468.26026294,
             0.00012863,
             0.00011545],
            ['tIOTUSD',
             0.95969,
             24306.55703175,
             0.96214,
             60186.47595187,
             -0.03534,
             -0.0355,
             0.95925,
             13274504.88034301,
             0.99459, 0.90661]
        ])
        tickers_response = self.client.tickers(['tIOTBTC', 'tIOTUSD'])
        self.assertIsInstance(tickers_response, list)

    @patch.object(requests, 'post')
    def testm3_shoud_have_ticker(self, mockpost):
        """test method 3/34 ticker"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            0.00011989,
            224267.1563644,
            0.00012015,
            265388.46405117,
            -8.12e-06,
            -0.0634,
            0.00012,
            3206446.72556849,
            0.00012812,
            0.00011545
        ])
        ticker_response = self.client.ticker('tIOTBTC')
        self.assertIsInstance(ticker_response, list)


    @patch.object(requests, 'post')
    def testm4_shoud_have_trades(self, mockpost):
        """test method 4/34 trades"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            [272147102, 1532428225632, -10.93936053, 0.00012022],
            [272147036, 1532428201910, -260.98846449, 0.00012028]
        ])
        trades_response = self.client.trades('tIOTUSD')
        self.assertIsInstance(trades_response, list)

    @patch.object(requests, 'post')
    def testm5_shoud_have_books(self, mockpost):
        """test method 5/34 books"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            [0.97692, 2, 1476.41706974],
            [0.97446, 1, 162.69181129],
            [0.97428, 3, 471.48294762]
        ])
        books_response = self.client.books('tIOTUSD', 'P1')
        self.assertIsInstance(books_response, list)

    @patch.object(requests, 'post')
    def testm6_shoud_have_stats(self, mockpost):
        """test method 6/34 stats"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            [1532430780000, 548711270.8708785],
            [1532430720000, 546414815.6475447],
            [1532430660000, 545031610.6767836]
        ])
        params = {
            'key'     : 'funding.size',
            'size'    : '1m',
            'symbol'  : 'fUSD',
            'section' : 'hist',
            'sort'    : '0'
        }
        stats_response = self.client.stats(**params)
        self.assertIsInstance(stats_response, list)

    @patch.object(requests, 'post')
    def testm7_shoud_have_candles(self, mockpost):
        """test method 7/34 candles"""
        mockresponse = Mock()
        mockpost.return_value = mockresponse
        mockresponse.text = json.dumps([
            [1532431320000, 8140.8, 8138.1, 8144, 8138, 15.50046363],
            [1532431260000, 8140.1, 8139.9, 8143.9, 8138.00802545, 29.16099656]
        ])
        candles_response = self.client.candles("1m", "tBTCUSD", "hist", limit='1')
        self.assertIsInstance(candles_response, list)
