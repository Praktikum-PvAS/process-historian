import unittest

from influxdb_client import Point

from cloudBuffer.buffer import Buffer


class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.valid_connection_params = {
            "host": "localhost",
            "organization": "TUD",
            "bucket": "my_bucket",
            "port": 8086,
            "token": "my_token"
        }
        self.test_buffer = Buffer(1000, self.valid_connection_params)

    def test_constructor(self):
        with self.assertRaises(ValueError):
            buffer = Buffer(None, self.valid_connection_params)
        with self.assertRaises(ValueError):
            buffer = Buffer(0, self.valid_connection_params)
        with self.assertRaises(ValueError):
            buffer = Buffer(-2, self.valid_connection_params)

        buffer = Buffer(1, self.valid_connection_params)

    def test_append_valid_insert(self):
        # https://github.com/influxdata/influxdb-client-python/blob/0c1d1d9ff92dd2b3b4a9b6aa1e8f5b1c02fd48ab/influxdb_client/client/write/point.py#L80
        # possible Timestamps
        self.test_buffer.append("node_name", [("tag_a", "tag")],
                                [("value", 1)], "2009-11-10T23:00:00.123456Z")
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 1)

    def test_append_invalid_node_name_insert(self):
        with self.assertRaises(ValueError):
            self.test_buffer.append("", [("tag_a", "tag")], [("value", 1)],
                                    "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            self.test_buffer.append(None, [("tag_a", "tag")],
                                    [("value", 1)],
                                    "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_value_insert(self):
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")], None,
                                    "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")], [],
                                    "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_timestamp_insert(self):
        with self.assertRaises(ValueError):
            self.test_buffer.append("node_name", [("tag_a", "tag")],
                                    [("value", 1)], None)

    def test_append_many(self):
        points = []
        for i in range(10):
            points.append(("node_name", [("tag_a", "tag")], [("value", 1)],
                           "2009-11-10T23:00:00.123456Z"))
        self.test_buffer.append_many(points)
        self.assertEqual(len(self.test_buffer._Buffer__buffer), 10)

    def test_append_many_invalid(self):
        # Name
        points = [("", [("tag_a", "tag")], [("value", 1)],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        points = [(None, [("tag_a", "tag")], [("value", 1)],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        # Value
        points = [("node_name", [("tag_a", "tag")], [],
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        points = [("node_name", [("tag_a", "tag")], None,
                   "2009-11-10T23:00:00.123456Z")]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)
        # Timestamp
        points = [("node_name", [("tag_a", "tag")], [("value", 1)], None)]
        with self.assertRaises(ValueError):
            self.test_buffer.append_many(points)

    def test_max_buffer_length(self):
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


if __name__ == '__main__':
    unittest.main()
