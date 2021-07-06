import threading
import unittest
from simulation_server import run_simulation_server
from opcuaClient.opcuaClient import Client
import json


class OPCUATest(unittest.TestCase):
    def setUp(self):
        self.appended_points = 0
        with open("./opcua_config.json", "r") as opcua_conf:
            self.config = json.load(opcua_conf)
        self.opcua = Client(self.config, self.callback)

    def callback(self, a, b, c, d):
        self.appended_points = self.appended_points + 1

    def test_construct(self):
        # Use "none" as config
        # Use an invalid config
        # Use "none" as callable
        # Use an int as callable
        # ^ All of these should raise ValueError
        # self.assertRaises(ValueError, lambda: Client(.....))
        #
        # Create a client with valid attributes
        self.fail("Needs implementation")

    def test_connect_disconnect(self):
        # Test self.opcua.connect() (raises Exception)
        # Test self.opcua.disconnect() (raises Exception)
        # Start server
        # Test self.opcua.disconnect() (raises Exception)
        # Test self.opcua.connect()
        # Test self.opcua.connect() (don't know what happens here)
        # Test self.opcua.disconnect()
        # Wait for server to finish
        self.fail("Needs implementation")

    def test_get_intervals(self):
        # Start server
        # Connect
        # Test self.opcua.get_intervals()
        self.fail("Needs implementation")

    def test_poll(self):
        server_thread = threading.Thread(target=run_simulation_server,
                                         args=[2])
        server_thread.start()
        self.opcua.connect()
        self.opcua.poll(1000)
        self.opcua.disconnect()
        self.assertEqual(self.appended_points, 2)
        server_thread.join()

    def test_poll_server_status(self):
        # Test self.opcua.poll_server_status()
        self.fail("Needs implementation")

    def test_subscribe_all(self):
        # Start server with 1 or 2 steps
        # subscribe_all()
        # Wait for server to finish
        # Check self.appended_points
        self.fail("Needs implementation")


if __name__ == '__main__':
    unittest.main()
