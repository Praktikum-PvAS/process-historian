import unittest

from influxdb_client import Point

from cloudBuffer.buffer import Buffer


# TODO Necessary to insert a test function for each case? (None, int, Str, ...)?
# TODO What to add to avoid bare except?


class MyTestCase(unittest.TestCase):
    def test_append_valid_insert(self):
        # try catch
        # https://github.com/influxdata/influxdb-client-python/blob/0c1d1d9ff92dd2b3b4a9b6aa1e8f5b1c02fd48ab/influxdb_client/client/write/point.py#L80
        # possible Timestamps
        my_connection_params = {
            "host": "localhost",
            "username": "root",
            "password": "root",
            "organization": "TUD",
            "bucket": "",
            "port": 8086
        }

        test_point = Point("node_name")
        test_point.tag("tag_a", "tag_b")
        test_point.field("value", 1)
        test_point.time("2009-11-10T23:00:00.123456Z")

        my_buffer = Buffer(my_connection_params)
        my_buffer.append("node_name", [("tag_a", "tag_b")], 1, "2009-11-10T23:00:00.123456Z")
        self.assertEquals(my_buffer._Buffer__buffer[-1], test_point)

    def test_append_invalid_node_name_insert(self):
        my_connection_params = {
            "host": "localhost",
            "username": "root",
            "password": "root",
            "organization": "TUD",
            "bucket": "",
            "port": 8086
        }
        my_buffer = Buffer(my_connection_params)
        with self.assertRaises(ValueError):
            my_buffer.append("", [("tag_a", "tag_b")], 1, "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            my_buffer.append(None, [("tag_a", "tag_b")], 1, "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_tag_insert(self):
        my_connection_params = {
            "host": "localhost",
            "username": "root",
            "password": "root",
            "organization": "TUD",
            "bucket": "",
            "port": 8086
        }
        my_buffer = Buffer(my_connection_params)
        with self.assertRaises(ValueError):
            my_buffer.append("node_name", None, 1, "2009-11-10T23:00:00.123456Z")
        with self.assertRaises(ValueError):
            my_buffer.append("node_name", [], 1, "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_value_insert(self):
        my_connection_params = {
            "host": "localhost",
            "username": "root",
            "password": "root",
            "organization": "TUD",
            "bucket": "",
            "port": 8086
        }
        my_buffer = Buffer(my_connection_params)
        with self.assertRaises(ValueError):
            my_buffer.append("node_name", [("tag_a", "tag_b")], [], "2009-11-10T23:00:00.123456Z")

    def test_append_invalid_timestamp_insert(self):
        my_connection_params = {
            "host": "localhost",
            "username": "root",
            "password": "root",
            "organization": "TUD",
            "bucket": "",
            "port": 8086
        }
        my_buffer = Buffer(my_connection_params)
        with self.assertRaises(ValueError):
            my_buffer.append("node_name", [("tag_a", "tag_b")], 1, None)

    def test_valid_write_points(self):
        my_buffer = Buffer()
        my_buffer.append("node_name", 1, "2009-11-10T23:00:00.123456Z")
        with self.assertRaises():
            my_buffer.write_points()

    # TODO How to show invalid test?
    def test_invalid_write_points(self):
        pass


if __name__ == '__main__':
    unittest.main()
