#######################################################################################
#    Title: test_opcua_listener source code
#    Author: Valentin Khaydarov
#    Date: 23.01.2021
#    Code version: 511435a
#    Availability: https://github.com/Praktikum-PvAS/planteye-nebula/blob/57616be37af3aee143826c7fca484592c4c27e65/tests/test_opcua_listener.py
#
#    MIT License
#
#    Copyright (c) 2021 Valentin Khaydarov
#    Copyright (c) 2021 Max Kirchner, Patrick Suwinski
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#######################################################################################
import time
import unittest
import threading
import json

import influxdb_client

from simulation_server import run_simulation_server
from cloudBuffer.buffer import Buffer
from opcuaClient.opcuaClient import Client


class OPCUAIntegrationTest(unittest.TestCase):
    def setUp(self):
        with open("./opcua_config.json", "r") as opcua_conf:
            self.config = json.load(opcua_conf)
        self.buffer = Buffer(1000, {
            "bucket": "bucket",
            "host": "http://example.com",
            "organization": "organization",
            "token": "token"
        })
        self.opcua = Client(self.config, self.buffer.append)

    def start_sim_server(self, steps: int):
        ready = threading.Event()
        self.server_thread = threading.Thread(target=run_simulation_server,
                                              args=[steps, ready])
        self.server_thread.start()
        ready.wait(30)  # Waits until server is ready, timeout in seconds

    def wait_for_sim_server(self):
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join()

    def test_integration_poll(self):
        self.assertEqual(0, len(self.buffer._Buffer__buffer))
        self.start_sim_server(5)
        try:
            self.opcua.connect()
            self.opcua.poll(1000)
            self.assertEqual(2, len(self.buffer._Buffer__buffer))
            self.assertIsInstance(self.buffer._Buffer__buffer[0], influxdb_client.Point)
            self.assertIsInstance(self.buffer._Buffer__buffer[1], influxdb_client.Point)
        finally:
            self.opcua.disconnect()
            self.wait_for_sim_server()

    def test_integration_subscribe(self):
        # Use self.buffer._Buffer__buffer to get the buffer
        # Check buffer length = 0
        self.assertEqual(0, len(self.buffer._Buffer__buffer))
        # Start server
        self.start_sim_server(2)
        try:
            self.opcua.connect()
            self.opcua.subscribe_all()
            time.sleep(2.2)
            self.opcua.disconnect()
            # expected: first value + 2 further values from the server
            self.assertEqual(3, len(self.buffer._Buffer__buffer))
            self.assertIsInstance(self.buffer._Buffer__buffer[0], influxdb_client.Point)
            self.assertIsInstance(self.buffer._Buffer__buffer[1], influxdb_client.Point)
            self.assertIsInstance(self.buffer._Buffer__buffer[2], influxdb_client.Point)
        finally:
            self.wait_for_sim_server()
