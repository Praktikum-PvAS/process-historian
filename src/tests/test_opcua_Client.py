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
        self.appended_points = 0
        cfg_f = Path(os.path.dirname(
            os.path.realpath(__file__))) / "opcua_config.json"
        with open(cfg_f, "r") as opcua_conf:
            self.config = json.load(opcua_conf)
        self.opcua = Client(self.config, self.callback, self.callback_many)

    def callback(self, a, b, c, d):
        self.appended_points = self.appended_points + 1

    def callback_many(self, a):
        self.appended_points = self.appended_points + len(a)

    def start_sim_server(self, steps: int):
        ready = threading.Event()
        self.server_thread = threading.Thread(target=run_simulation_server,
                                              args=[steps, ready])
        self.server_thread.start()
        ready.wait(30)  # Waits until server is ready, timeout in seconds

    def wait_for_sim_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()

    def test_construct(self):
        with self.assertRaises(ValueError):
            client = Client(None, self.callback, self.callback_many)
        with self.assertRaises(KeyError):
            client = Client({}, self.callback, self.callback_many)
        with self.assertRaises(ValueError):
            client = Client(self.config, None, self.callback_many)
        with self.assertRaises(ValueError):
            client = Client(self.config, 1, self.callback_many)
        with self.assertRaises(ValueError):
            client = Client(self.config, self.callback, None)
        with self.assertRaises(ValueError):
            client = Client(self.config, self.callback, 1)
        client = Client(self.config, self.callback, self.callback_many)

    def test_connect_disconnect(self):
        self.opcua.connect()
        self.opcua.disconnect()
        self.start_sim_server(5)
        try:
            self.opcua.disconnect()
            self.opcua.connect()
            self.opcua.connect()
            self.opcua.disconnect()
        finally:
            self.wait_for_sim_server()

    def test_get_intervals(self):
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.assertEqual([1000], self.opcua.get_intervals())
        finally:
            self.wait_for_sim_server()

    def test_poll(self):
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.opcua.poll(1000)
            self.opcua.disconnect()
            self.assertEqual(self.appended_points, 2)
        finally:
            self.wait_for_sim_server()

    def test_poll_server_status(self):
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.assertEqual(0, self.opcua.poll_server_status())
        finally:
            self.opcua.disconnect()
            self.wait_for_sim_server()

    def test_subscribe_all(self):
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
