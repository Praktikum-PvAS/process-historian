import unittest

import opcua

from opcuaClient.opcuaClient import CustomNode, Client


class MyTestCase(unittest.TestCase):
    def test_something(self):
        self.assertEqual(True, False)

    def test_unexpected_assembly_type_custom_node(self):
        node = opcua.Node("", 1)
        with self.assertRaises(ValueError):
            test_node = CustomNode("unexpected", "", "", node)

    def test_opc_client_config_missing(self):
        with self.assertRaises(ValueError):
            test_client = Client(None, lambda a: a + 2)

    def test_opc_client_wrong_callback(self):
        with self.assertRaises(ValueError):
            test_client = Client({}, [])


if __name__ == '__main__':
    unittest.main()
