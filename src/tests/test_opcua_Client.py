import threading
import time
import unittest
from pathlib import Path
import os.path

from simulation_server import run_simulation_server
from opcuaClient.opcuaClient import Client
import json


class OPCUATest(unittest.TestCase):
    def setUp(self):
        """
        Initialise the OPC UA Client for each test.
        """
        self.appended_points = 0
        cfg_f = Path(os.path.dirname(
            os.path.realpath(__file__))) / "opcua_config.json"
        with open(cfg_f, "r") as opcua_conf:
            self.config = json.load(opcua_conf)
        self.opcua = Client(self.config, self.callback, self.callback_many)
        # Wait 2 seconds before every test
        time.sleep(2)

    def callback(self, _a, _b, _c, _d):
        """
        Counts how often the callback is called
        """
        self.appended_points = self.appended_points + 1

    def callback_many(self, a):
        self.appended_points = self.appended_points + len(a)

    def start_sim_server(self, steps: int):
        """
        Starts the simulation server with a specific number of steps.
        :param steps: number of steps
        """
        ready = threading.Event()
        self.server_thread = threading.Thread(target=run_simulation_server,
                                              args=[steps, ready])
        self.server_thread.start()
        ready.wait(30)  # Waits until server is ready, timeout in seconds

    def wait_for_sim_server(self):
        """
        Joins the simulation server thread and waits until it is
        terminated.
        """
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()

    def test_construct_config_invalid(self):
        """
        Tests config validation
        """
        with self.assertRaises(ValueError):
            _client = Client(None, self.callback, self.callback_many)
        with self.assertRaises(KeyError):
            _client = Client({}, self.callback, self.callback_many)

    def test_construct_cb_invalid(self):
        """
        Tests callback validation
        """
        with self.assertRaises(ValueError):
            _client = Client(self.config, None, self.callback_many)
        with self.assertRaises(ValueError):
            _client = Client(self.config, 1, self.callback_many)

    def test_construct_cb_many_invalid(self):
        """
        Tests callback_many validation
        """
        with self.assertRaises(ValueError):
            _client = Client(self.config, self.callback, None)
        with self.assertRaises(ValueError):
            _client = Client(self.config, self.callback, 1)

    def test_construct_valid(self):
        """
        Tests constructor when all parameters are valid
        """
        _client = Client(self.config, self.callback, self.callback_many)

    def test_connect_disconnect(self):
        """
        Tests if it is possible to connect to and disconnect from the OPC
        UA server:
        a) if no server is started
        b) if a server is started
        """
        self.opcua.connect()
        self.opcua.disconnect(log=False)
        self.start_sim_server(5)
        try:
            self.opcua.disconnect(log=False)
            self.opcua.connect()
            with self.assertRaises(ConnectionError):
                self.opcua.connect()
            self.opcua.disconnect(log=False)
        finally:
            self.wait_for_sim_server()

    def test_get_intervals(self):
        """
        Tests if the interval is transmitted correctly
        """
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.assertEqual([1000], self.opcua.get_intervals())
        finally:
            self.opcua.disconnect()
            self.wait_for_sim_server()

    def test_poll(self):
        """
        Tests if the poll function is executable and if it is executed
         as often as expected.
        """
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.opcua.poll(1000)
        finally:
            self.opcua.disconnect()
            self.wait_for_sim_server()
            self.assertEqual(self.appended_points, 2)

    def test_poll_server_status(self):
        """
        Tests whether the server status can be queried and its correctness.
        """
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.assertEqual(0, self.opcua.poll_server_status())
        finally:
            self.opcua.disconnect()
            self.wait_for_sim_server()

    def test_subscribe_all(self):
        """
        Tests whether the client can subscribe to all nodes and the
        number of value changes is detected correctly.
        """
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.opcua.subscribe_all()
            time.sleep(2.2)
        finally:
            self.opcua.unsubscribe_all()
            self.opcua.disconnect()
            self.wait_for_sim_server()
        # expected: first value + 2 further values from the server
        self.assertEqual(3, self.appended_points)


if __name__ == '__main__':
    unittest.main()
