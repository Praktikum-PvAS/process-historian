import opcua
import time


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.opcua_config = opcua_config
        self.url = self.opcua_config["host"]
        self.opcua_lib_client = opcua.Client(self.url)
        self.callback = callback
        self.subHandler = SubscriptionHandler()
        self.nodes2poll = []
        self.nodes2sub = []
        self.init_lists()
        self.subscription_list = []

    def connect(self):
        try:
            self.opcua_lib_client.connect()
        except ConnectionError:
            print("OPCUA-Client was not able to connect to server!")
            # TODO errorhandling

    def disconnect(self):
        try:
            self.opcua_lib_client.disconnect()
        except ConnectionError:
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
                    self.nodes2poll.append([self.opcua_lib_client.get_node(nodes.nodeId), nodes.interval])
                elif nodes.mode == "subscription":
                    self.nodes2sub.append(self.opcua_lib_client.get_node(nodes.nodeId))

    def poll(self):
        # return to callback
        values = self.opcua_lib_client.get_values(self.nodes2poll[:, 0])
        # TODO how to call back?
        self.callback()  # returns the value to a callback function
        # TODO keep interval in mind

    def subscribe(self, node):
        # create one subscription and let subHandler watch it
        subscription = self.opcua_lib_client.create_subscription(100, self.subHandler)
        # subscribe to node
        handle = subscription.subscribe_data_change(node)
        self.subscription_list.append([node, subscription, handle])

    def unsubscribe(self, node):
        for i in range(len(self.subscription_list)):
            # search for handle
            if self.subscription_list[i][0] is node:
                # use handle to unsubscribe
                self.subscription_list[i][1].unsubscribe(self.subscription_list[i][2])
                # delete obsolete subscription
                del self.subscription_list[i][:]
                return


class SubscriptionHandler:
    def __init__(self, server, data_callback: callable):
        self.data_callback = data_callback
        self.server = server

    def datachange_notification(self, node: opcua.Node, value, raw_data):
        # Save data with callback
        self.data_callback(value)  # TODO how is input in callback

    # def event_notification(self, event):
