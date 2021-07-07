import unittest

from cloudBuffer.influxWrapper import InfluxWrapper


class MyTestCase(unittest.TestCase):
    # TODO: Add tests for invalid connections parameters
    def test_insert_many(self):
        my_connection_params = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        my_influx_wrapper = InfluxWrapper(my_connection_params)
        with self.assertRaises(ValueError):
            my_influx_wrapper.insert_many(None)

    def test_insert_many_2(self):
        my_connection_params = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        my_influx_wrapper = InfluxWrapper(my_connection_params)
        with self.assertRaises(ValueError):
            points = []
            my_influx_wrapper.insert_many(points)

    def test_insert(self):
        my_connection_params = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "A",
            "port": 8086,
            "token": "my_token"
        }
        my_influx_wrapper = InfluxWrapper(my_connection_params)
        with self.assertRaises(ValueError):
            my_influx_wrapper.insert(None)


if __name__ == '__main__':
    unittest.main()
