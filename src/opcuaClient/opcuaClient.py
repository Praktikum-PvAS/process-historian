import opcua
import time


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.opcua_config = opcua_config
        self.url = self.opcua_config["host"]
        self.opcua_lib_client = opcua.Client(self.url)
        self.callback = callback
        self.subHandler = SubscriptionHandler()
        self.nodes2poll = {}  # dictionary with [interval] = list<nodes>
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
                    # get interval and node
                    interval = node_attributes.interval
                    node = self.opcua_lib_client.get_node(node_attributes.nodeId)
                    # append the node and interval to the list in the dictionary
                    temp_list = self.nodes2poll.get(interval, [])
                    temp_list.append(node)
                    # store the list in the dict
                    self.nodes2poll[interval] = temp_list
                elif node_attributes.mode == "subscription":
                    self.nodes2sub.append(self.opcua_lib_client.get_node(node_attributes.nodeId))

    def get_intervals(self):
        # return all existing polling intervals from the polling dictionary
        return self.nodes2poll.keys()

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
        callback_dict = {node.nodeid: value}
        self.data_callback(callback_dict)

    # def event_notification(self, event):
