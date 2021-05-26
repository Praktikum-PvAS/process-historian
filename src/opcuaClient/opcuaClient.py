import opcua
import time


class Client:
    def __init__(self, config):
        self.opcua_config = config
        url = "unsere URL"  # TODO find out used url / get url out of config?
        self.opcua_lib_client = opcua.Client(self.opcua_config)

    def create_client(self):
        pass

    def connect(self):
        self.opcua_lib_client.connect()

    def disconnect(self):
        self.opcua_lib_client.disconnect()

    def poll(self):
        # TODO
        pass

    def subscribe(self):
        # TODO
        pass


