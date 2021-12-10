from unittest import mock
import pyactiveresource
import shopify
from tap_shopify.context import Context
from tap_shopify.streams.base import Stream
from tap_shopify.streams.inventory_items import InventoryItems
from tap_shopify.streams.inventory_levels import InventoryLevels
from tap_shopify.streams.locations import Locations
from tap_shopify.streams.order_refunds import OrderRefunds
from tap_shopify.streams.transactions import Transactions
from tap_shopify.streams.abandoned_checkouts import AbandonedCheckouts
from tap_shopify.streams.metafields import Metafields
from tap_shopify.streams.metafields import get_metafields
import unittest

class TestTimeoutValue(unittest.TestCase):
    """
        Verify the timeout value is set as expected by the tap
    """

    def test_timeout_value_not_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 300)

    def test_timeout_int_value_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50,
            "request_timeout": 100
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 100)

    def test_timeout_string_value_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50,
            "request_timeout": "100"
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 100)

    def test_timeout_empty_value_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50,
            "request_timeout": ""
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 300)

    def test_timeout_0_value_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50,
            "request_timeout": 0.0
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 300)

    def test_timeout_string_0_value_passed_in_config(self):
        # initialize config
        Context.config = {
            "start_date": "2021-01-01",
            "api_key": "test_api_key",
            "shop": "test_shop",
            "results_per_page": 50,
            "request_timeout": "0.0"
        }

        # initialize base class
        stream = Stream()
        # verify the timeout is set as expected
        self.assertEquals(stream.request_timeout, 300)

class TestTimeoutBackoff(unittest.TestCase):
    """
        Verify the tap backoff for 5 times when timeout error occurs
    """

    @mock.patch("time.sleep")
    @mock.patch("shopify.Checkout.find")
    def test_AbandonedCheckouts_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize 'AbandonedCheckouts' as it calls the function 'call_api' from the base class
        abandoned_checkouts = AbandonedCheckouts()
        try:
            # function call
            abandoned_checkouts.call_api({})
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("shopify.InventoryItem.find")
    def test_InventoryItems_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize class
        inventory_items = InventoryItems()
        try:
            # function call
            inventory_items.get_inventory_items([1, 2, 3])
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("pyactiveresource.activeresource.ActiveResource.find")
    def test_InventoryLevels_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize class
        inventory_levels = InventoryLevels()
        try:
            # function call
            inventory_levels.api_call_for_inventory_levels(1, 'test')
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("pyactiveresource.activeresource.ActiveResource.find")
    def test_Locations_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize class
        locations = Locations()
        try:
            # function call
            locations.replication_object.find()
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("shopify.Order.metafields")
    def test_Metafields_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        try:
            # function call
            get_metafields(shopify.Order, 1, shopify.Order, 100)
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("shopify.Refund.find")
    def test_OrderRefunds_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize class
        order_refunds = OrderRefunds()
        try:
            # function call
            order_refunds.get_refunds(shopify.Product, 1)
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)

    @mock.patch("time.sleep")
    @mock.patch("pyactiveresource.activeresource.ActiveResource.find")
    def test_Transactions_timeout_backoff(self, mocked_find, mocked_sleep):
        # mock 'find' and raise timeout error
        mocked_find.side_effect = pyactiveresource.connection.Error('urlopen error _ssl.c:1074: The handshake operation timed out')

        # initialize class
        locations = Transactions()
        try:
            # function call
            locations.replication_object.find()
        except pyactiveresource.connection.Error:
            pass

        # verify we backoff 5 times
        self.assertEquals(mocked_find.call_count, 5)
