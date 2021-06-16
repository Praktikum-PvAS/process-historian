import unittest
from cloudBuffer.buffer import Buffer

# TODO Necessary to insert a test function for each case? (None, int, Str, ...)?
# TODO What to add to avoid bare except?


class MyTestCase(unittest.TestCase):
    def test_append_valid_insert(self):
        # try catch
        # https://github.com/influxdata/influxdb-client-python/blob/0c1d1d9ff92dd2b3b4a9b6aa1e8f5b1c02fd48ab/influxdb_client/client/write/point.py#L80
        # possible Timestamps
        try:
            my_connection_params = {
                "host": "localhost",
                "username": "root",
                "password": "root",
                "organization": "TUD",
                "bucket": "",
                "port": 8086
            }
            my_buffer = Buffer(my_connection_params)
            my_buffer.append("node_name", 1, "2009-11-10T23:00:00.123456Z")
        except:
            self.fail("invalid insert")

    def test_append_invalid_node_name_insert(self):
        try:
            my_connection_params = {
                "host": "localhost",
                "username": "root",
                "password": "root",
                "organization": "TUD",
                "bucket": "",
                "port": 8086
            }
            my_buffer = Buffer(my_connection_params)
            my_buffer.append("", 1, "2009-11-10T23:00:00.123456Z")
            my_buffer.append(None, 1, "2009-11-10T23:00:00.123456Z")
            my_buffer.append(1, 1, "2009-11-10T23:00:00.123456Z")
        except:
            self.fail("invalid insert")

    def test_append_invalid_value_insert(self):
        try:
            my_connection_params = {
                "host": "localhost",
                "username": "root",
                "password": "root",
                "organization": "TUD",
                "bucket": "",
                "port": 8086
            }
            my_buffer = Buffer(my_connection_params)
            my_buffer.append("node_name", None, "2009-11-10T23:00:00.123456Z")
            my_buffer.append("node_name", "123", "2009-11-10T23:00:00.123456Z")
        except:
            self.fail("invalid insert")

    def test_append_invalid_timestamp_insert(self):
        try:
            my_connection_params = {
                "host": "localhost",
                "username": "root",
                "password": "root",
                "organization": "TUD",
                "bucket": "",
                "port": 8086
            }
            my_buffer = Buffer(my_connection_params)
            my_buffer.append("node_name", 1, None)
            my_buffer.append("node_name", 1, "")
        except:
            self.fail("invalid insert")

    def test_valid_write_points(self):
        my_buffer = Buffer()
        my_buffer.append("node_name", 1, "2009-11-10T23:00:00.123456Z")
        try:
            my_buffer.write_points()
        except:
            self.fail("point couldn't write point")

    # TODO How to show invalid test?
    def test_invalid_write_points(self):
        pass


if __name__ == '__main__':
    unittest.main()
