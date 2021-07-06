import threading
import unittest
from test_simulation_server import run_simulation_server
from opcuaClient.opcuaClient import Client
import json

class MyTestCase(unittest.TestCase):
    def setUp(self):
        self.appended_points = 0
        self.config = self.parse_opcua_conf()
        self.opcua = Client(self.config, self.callback)
        # self.server = run_simulation_server(5)

    def callback(self, a, b, c, d):
        self.appended_points = self.appended_points + 1

    def parse_opcua_conf(self):
        try:
            with open("./opcua_config.json", "r") as opcua_conf:
                conf = json.load(opcua_conf)
                return conf
        except (FileExistsError, PermissionError):
            print("Can't read opcua config! Make sure you have the " +
                  "right permissions and the file exists")
            exit()

        if "host" not in self.__opcua_conf:
            print("Key \"host\" not found in opcua config.")
            print("Your opcua config seems to be incorrect or incomplete.")
            exit()

    # TODO: start server in separate thread?
    def test_reading(self):
        # self.server.start()  # or in separate thread
        server_thread = threading.Thread(target=run_simulation_server, args=[20])
        server_thread.start()
        self.opcua.connect()
        self.opcua.poll(1000)  # value from config
        self.opcua.disconnect()
        server_thread.join()
        # self.server.stop()
        self.assertEqual(self.appended_points, 1)

if __name__ == '__main__':
    unittest.main()
