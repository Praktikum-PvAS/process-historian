import opcua
import time


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.opcua_config = opcua_config
        self.url = self.opcua_config["host"]
        self.opcua_lib_client = opcua.Client(self.opcua_config)
        self.callback = callback
        self.subHandler = SubscriptionHandler()
        self.nodes2poll = []
        self.nodes2sub = []
        self.init_lists()

    def connect(self):
        try:
            self.opcua_lib_client.connect()
        except:
            print("OPCUA-Client was not able to connect to server!")
            # TODO errorhandling

    def disconnect(self):
        try:
            self.opcua_lib_client.disconnect()
        except:
            print("OPCUA-Client was not able to disconnect from server!")
            # TODO errorhandling

    def init_lists(self):
        # get every node from config
        type_list = ["sensors", "actuators", "services"]
        for node_type in type_list:
            # search for every node of that type
            nodes = self.opcua_config[node_type]["attributes"]
            for nodes in nodes:
                if nodes.mode == "poll":
                    self.nodes2poll.append(self.opcua_lib_client.get_node(nodes.nodeId), nodes.interval)
                elif nodes.mode == "subscription":
                    self.nodes2sub.append(self.opcua_lib_client.get_node(nodes.nodeId))

    def poll(self):
        # return to callback
        values = self.opcua_lib_client.get_values(self.nodes2poll[:, 0])
        self.callback(values)  # returns the value to a callback function
        # TODO keep interval in mind

    def subscribe(self, nodes):
        subscription = self.opcua_lib_client.create_subscription(100, self.subHandler())
        subscription.subscribe_data_change(nodes)


class SubscriptionHandler:
    def __init__(self, server, data_callback: callable):
        self.data_callback = data_callback
        self.sub_handler = SubscriptionHandler()
        self.server = server
        self.subscription = opcua.Subscription(self, server, )

    def datachange_notification(self, node: opcua.Node, value, raw_data):
        # TODO
        pass

