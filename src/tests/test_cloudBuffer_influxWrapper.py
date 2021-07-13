import unittest

from cloudBuffer.influxWrapper import InfluxWrapper


class InfluxWrapperTest(unittest.TestCase):

    def setUp(self):
        """
        setUp method
        """
        self.valid_connection_params = {
            "host": "http://localhost",
            "organization": "TUD",
            "bucket": "A",
            "token": "my_token"
        }

        self.influxWrapper = InfluxWrapper(self.valid_connection_params)

    def test_connection_params(self):
        """
        Test constructor with valid and invalid connection_params
        """
        # all params ok
        my_influx_wrapper = InfluxWrapper(self.valid_connection_params)
        # one data missing
        with self.assertRaises(KeyError):
            my_influx_wrapper = InfluxWrapper({})
        # host not set
        invalid_connection_params = {
            "host": None,
            "organization": "TUD",
            "bucket": "A",
            "token": "my_token"
        }
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["host"] = ""
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        # organization not set
        invalid_connection_params["host"] = "http://localhost"
        invalid_connection_params["organization"] = None
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["organization"] = ""
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        # no bucket set
        invalid_connection_params["organization"] = "TUD"
        invalid_connection_params["bucket"] = None
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["bucket"] = ""
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        # no token set
        invalid_connection_params["bucket"] = "A"
        invalid_connection_params["token"] = None
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["token"] = ""
        with self.assertRaises(ValueError):
            my_influx_wrapper = InfluxWrapper(invalid_connection_params)

    def test_insert_many_invalid(self):
        """
        Test insert_many method with invalid parameters
        """
        with self.assertRaises(ValueError):
            self.influxWrapper.insert_many(None)
        with self.assertRaises(ValueError):
            points = []
            self.influxWrapper.insert_many(points)

    def test_insert(self):
        """
        Test insert method with invalid parameters
        """
        with self.assertRaises(ValueError):
            self.influxWrapper.insert(None)


if __name__ == '__main__':
    unittest.main()
