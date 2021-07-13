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

    def test_constructor_valid(self):
        """
        Test constructor with valid connection_params
        """
        _my_influx_wrapper = InfluxWrapper(self.valid_connection_params)

    def test_constructor_none(self):
        """
        Test constructor with empty connection_params
        """
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(None)
        with self.assertRaises(KeyError):
            _influx_wrapper = InfluxWrapper({})

    def test_constructor_invalid_host(self):
        """
        Test constructor with invalid host in connection_params
        """
        invalid_connection_params = self.valid_connection_params

        invalid_connection_params["host"] = None
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["host"] = ""
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)

    def test_constructor_invalid_org(self):
        """
        Test constructor with invalid organization in connection_params
        """
        invalid_connection_params = self.valid_connection_params

        invalid_connection_params["organization"] = None
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["organization"] = ""
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)

    def test_constructor_invalid_bucket(self):
        """
        Test constructor with invalid bucket in connection_params
        """
        invalid_connection_params = self.valid_connection_params

        invalid_connection_params["bucket"] = None
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["bucket"] = ""
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)

    def test_constructor_invalid_token(self):
        """
        Test constructor with invalid token in connection_params
        """
        invalid_connection_params = self.valid_connection_params

        invalid_connection_params["token"] = None
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)
        invalid_connection_params["token"] = ""
        with self.assertRaises(ValueError):
            _influx_wrapper = InfluxWrapper(invalid_connection_params)

    def test_insert_many_invalid(self):
        """
        Test insert_many method with invalid parameters
        """
        with self.assertRaises(ValueError):
            self.influxWrapper.insert_many(None)
        with self.assertRaises(ValueError):
            points = []
            self.influxWrapper.insert_many(points)

    def test_insert_invalid(self):
        """
        Test insert method with invalid parameters
        """
        with self.assertRaises(ValueError):
            self.influxWrapper.insert(None)


if __name__ == '__main__':
    unittest.main()
