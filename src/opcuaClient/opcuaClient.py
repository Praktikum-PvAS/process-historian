import opcua
import time


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.opcua_config = opcua_config
        url = "unsere URL"  # TODO find out used url / get url out of config?
        self.opcua_lib_client = opcua.Client(self.opcua_config)
        self.callback = callback

    def create_client(self):
        pass

    def connect(self):
        self.opcua_lib_client.connect()

    def disconnect(self):
        self.opcua_lib_client.disconnect()

    def poll(self):
        # get every node from config
        list_nodes = []
        # sensors
        sensors = self.opcua_config["sensors"]["attributes"]
        for sensor in sensors:
            if sensor.mode == "poll":
                list_nodes.append(self.opcua_lib_client.get_node(sensor.nodeId))
        # actuators
        actuators = self.opcua_config["actuators"]["attributes"]
        for actuator in actuators:
            if actuator.mode == "poll":
                list_nodes.append(self.opcua_lib_client.get_node(actuator.nodeId))
        # services
        services = self.opcua_config["services"]["attributes"]
        for service in services:
            if service.mode == "poll":
                list_nodes.append(self.opcua_lib_client.get_node(service.nodeId))
        # return to callback
        values = self.opcua_lib_client.get_values(list_nodes)
        self.callback(values)  # returns the value to a callback function

    def subscribe(self):
        # TODO
        pass
