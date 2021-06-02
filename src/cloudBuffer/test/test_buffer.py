import unittest


class MyTestCase(unittest.TestCase):
    def test_valid_insert(self, node_name, value, timestamp):
        pass

    def test_valid_write_points(self):
        pass

    def test_invalid_node_name_insert(self, node_name, value, timestamp):
        pass

    def test_invalid_value_insert(self, node_name, value, timestamp):
        pass

    def test_invalid_timestamp_insert(self, node_name, value, timestamp):
        pass

    def test_invalid_write_points(self):
        pass

if __name__ == '__main__':
    unittest.main()
