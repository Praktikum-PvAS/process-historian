import opcua
import time


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.opcua_config = opcua_config
        self.url = self.opcua_config["host"]
        self.opcua_lib_client = opcua.Client(self.url)
        self.callback = callback
        self.subHandler = SubscriptionHandler()
        self.nodes2poll = {}    # dictionary with [interval] = list<nodes>
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
            nodes_attributes = self.opcua_config[node_type]["attributes"]
            for node_attributes in nodes_attributes:
                # add nodeId to the list
                if node_attributes.mode == "poll":
                    interval = node_attributes.interval
                    node = self.opcua_lib_client.get_node(node_attributes.nodeId)
                    # TODO check for duplication
                    # TODO do we have to initialize the list first?
                    self.nodes2poll[interval] = self.nodes2poll[interval].append(node)
                elif node_attributes.mode == "subscription":
                    self.nodes2sub.append(self.opcua_lib_client.get_node(node_attributes.nodeId))

    def poll(self, interval):
        # return to callback
        # TODO implement interval
        nodes = self.nodes2poll[interval]
        # get node ids
        nodeids = []
        for node in nodes:
            nodeids.append(node.nodeid)
        values = self.opcua_lib_client.get_values(nodes)
        # return a dic with values and nodeIds
        nodeid_value_pairs = dict(zip(nodeids, values))
        self.callback(nodeid_value_pairs)  # returns the value to a callback function

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
