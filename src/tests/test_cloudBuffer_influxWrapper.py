import unittest

from cloudBuffer.influxWrapper import InfluxWrapper


class MyTestCase(unittest.TestCase):

    def setUp(self):
        self.my_connection_params = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }

        self.influxWrapper = InfluxWrapper(self.my_connection_params)

    def test_connection_params(self):
        # all params ok
        my_influx_wrapper = InfluxWrapper(self.my_connection_params)
        # one data missing
        with self.assertRaises(KeyError):
            my_influx_wrapper = InfluxWrapper({})
        # host not set
        my_connection_params_nohost = {
            "host": None,
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nohost)
        my_connection_params_nohost2 = {
            "host": "",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nohost2)
        # organization not set
        my_connection_params_noorg = {
            "host": "localhost",
            "organization": None,
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_noorg)
        my_connection_params_noorg2 = {
            "host": "localhost",
            "organization": "",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_noorg2)
        # no bucket set
        my_connection_params_nobucket = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": None,
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nobucket)
        my_connection_params_nobucket2 = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "",
            "port": 8086,
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nobucket2)
        # no token set
        my_connection_params_nobucket = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": None
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nobucket)
        my_connection_params_nobucket2 = {
            "host": "localhost",
            "organization": "",
            "bucket": "A",
            "port": 8086,
            "token": ""
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(my_connection_params_nobucket2)

    def test_insert_many(self):
        my_influx_wrapper = InfluxWrapper(self.my_connection_params)
        with self.assertRaises(ValueError):
            my_influx_wrapper.insert_many(None)

    def test_insert_many_2(self):
        my_influx_wrapper = InfluxWrapper(self.my_connection_params)
        with self.assertRaises(ValueError):
            points = []
            my_influx_wrapper.insert_many(points)

    def test_insert(self):
        my_influx_wrapper = InfluxWrapper(self.my_connection_params)
        with self.assertRaises(ValueError):
            my_influx_wrapper.insert(None)


if __name__ == '__main__':
    unittest.main()
