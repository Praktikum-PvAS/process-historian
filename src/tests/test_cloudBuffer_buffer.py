import unittest

from cloudBuffer.buffer import Buffer


class CloudBufferTest(unittest.TestCase):
    def setUp(self):
        """
        setUp method
        """
        self.valid_connection_params = {
            "host": "http://localhost",
            "organization": "TUD",
            "bucket": "my_bucket",
            "port": 8086,
            "token": "my_token"
        }
        self.test_buffer = Buffer(1000, self.valid_connection_params)

    def test_constructor_max_buffer_len_invalid(self):
        """
        Tests invalid max_buffer_len constructor parameter
        """
        with self.assertRaises(ValueError):
            _buffer = Buffer(None, self.valid_connection_params)
        with self.assertRaises(ValueError):
            _buffer = Buffer(0, self.valid_connection_params)
        with self.assertRaises(ValueError):
            _buffer = Buffer(-2, self.valid_connection_params)

    def test_constructor_valid(self):
        _buffer = Buffer(1, self.valid_connection_params)

    def test_append_valid(self):
        """
        Tests the append method with valid parameters
        """
        self.test_buffer.append("node_name", [("tag_a", "tag")],
                                [("value", 1)], "2009-11-10T23:00:00.123456Z")
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 1)

    def test_append_invalid_measurement(self):
        """
        Tests the append method with an invalid measurement
        """
        with self.assertRaises(ValueError):
            self.test_buffer.append("", [("tag_a", "tag")], [("value", 1)],
                                    "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            self.test_buffer.append(None, [("tag_a", "tag")],
                                    [("value", 1)],
                                    "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_values(self):
        """
        Tests the append method with invalid values
        """
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")], None,
                                    "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")], [],
                                    "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_timestamp(self):
        """
        Tests the append method with an invalid timestamp
        """
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")],
                                    [("value", 1)], None)

    def test_append_many(self):
        """
        Tests the append_many method with valid parameters
        """
        points = []
        for i in range(10):
            points.append(("node_name", [("tag_a", "tag")], [("value", 1)],
                           "2009-11-10T23:00:00.123456Z"))
        self.test_buffer.append_many(points)
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 10)

    def test_append_many_invalid_measurement(self):
        """
        Tests the append_many method with a invalid measurements
        """
        points = [("", [("tag_a", "tag")], [("value", 1)],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        points = [(None, [("tag_a", "tag")], [("value", 1)],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)

    def test_append_many_invalid_values(self):
        """
        Tests the append_many method with invalid values
        """
        points = [("node_name", [("tag_a", "tag")], [],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        points = [("node_name", [("tag_a", "tag")], None,
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)

    def test_append_many_invalid_timestamp(self):
        """
        Tests the append_many method with an invalid timestamp
        """
        points = [("node_name", [("tag_a", "tag")], [("value", 1)], None)]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)

    def test_max_buffer_length(self):
        """
        Tests if the buffer respects the max_buffer_length
        """
        points = []
        for i in range(1050):
            points.append(("node_name", [("tag_a", "tag")], [("value", 1)],
                           "2009-11-10T23:00:00.123456Z"))
        self.test_buffer.append_many(points)
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 1000)

        self.test_buffer.append("node_name", [("tag_a", "tag")],
                                [("value", 1)], "2009-11-10T23:00:00.123456Z")
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 1000)

        points = []
        for i in range(10):
            points.append(("node_name", [("tag_a", "tag")], [("value", 1)],
                           "2009-11-10T23:00:00.123456Z"))
        self.test_buffer.append_many(points)
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 1000)

    def test_max_buffer_length_infinity(self):
        """
        Tests if an infinite buffer length works.
        Warning: When test_length is high this test needs a large amount
        of RAM to run!
        """
        test_length = 100000
        buffer = Buffer(-1, self.valid_connection_params)
        points = []
        for i in range(test_length):
            points.append(("node_name", [("tag_a", "tag")], [("value", 1)],
                           "2009-11-10T23:00:00.123456Z"))
        buffer.append_many(points)
        self.assertEqual(len(buffer._Buffer__buffer), test_length)

        buffer.append("node_name", [("tag_a", "tag")], [("value", 1)],
                      "2009-11-10T23:00:00.123456Z")
        self.assertEqual(len(buffer._Buffer__buffer), test_length + 1)


if __name__ == '__main__':
    unittest.main()
