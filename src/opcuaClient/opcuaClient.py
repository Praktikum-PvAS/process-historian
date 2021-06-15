import opcua


class Client:
    def __init__(self, opcua_config: dict, callback: callable):
        self.__opcua_config = opcua_config
        self.__url = self.__opcua_config["host"]
        self._opcua_lib_client = opcua.Client(self.__url)
        self.__callback = callback
        self.__subscription = None
        self.__subHandler = SubscriptionHandler(callback)
        self._nodes2poll = {}  # dictionary with [interval] = list<nodes>
        self._nodes2sub = []
        self.__subscription_handles = []
        self.__init_lists()

    def connect(self):
        try:
            self._opcua_lib_client.connect()
        except ConnectionError:
            print("OPC UA-Client was not able to connect to server!")

    def disconnect(self):
        try:
            self.unsubscribe_all()
            self._opcua_lib_client.disconnect()
        except ConnectionError:
            print("OPC UA-Client was not able to disconnect from server!")

    def __init_lists(self):
        # get every node from config
        type_list = ["sensors", "actuators", "services"]
        for node_type in type_list:
            # search for every node of that type
            nodes_attributes = self.__opcua_config[node_type]["attributes"]
            for node_attributes in nodes_attributes:
                # add nodeId to the list
                if node_attributes.mode == "poll":
                    # get interval and node
                    interval = node_attributes.interval
                    node = self._opcua_lib_client.get_node(
                        node_attributes.nodeId)
                    # append the node and interval to the list in the
                    # dictionary
                    temp_list = self._nodes2poll.get(interval, [])
                    temp_list.append(node)
                    # store the list in the dict
                    self._nodes2poll[interval] = temp_list
                elif node_attributes.mode == "subscription":
                    self._nodes2sub.append(
                        self._opcua_lib_client.get_node(node_attributes.nodeId))

    def get_intervals(self):
        # return all existing polling intervals from the polling dictionary
        return self._nodes2poll.keys()

    def poll(self, interval: int):
        nodes = self._nodes2poll[interval]
        # get node ids
        nodeids = []
        for node in nodes:
            nodeids.append(node.nodeid)
        values = self._opcua_lib_client.get_values(nodes)
        # return a dic with values and nodeIds
        nodeid_value_pairs = dict(zip(nodeids, values))
        self.__callback(
            nodeid_value_pairs)  # returns the value to a callback function

    def subscribe_all(self):
        # create one subscription and let subHandler watch it
        self.__subscription = self._opcua_lib_client\
            .create_subscription(100, self.__subHandler)
        # subscribe to node
        handles = self.__subscription.subscribe_data_change(self._nodes2sub)
        self.__subscription_handles = handles

    def unsubscribe_all(self):
        self.__subscription.unsubscribe(self.__subscription_handles)


class SubscriptionHandler:
    def __init__(self, data_callback: callable):
        self.__data_callback = data_callback

    def datachange_notification(self, node: opcua.Node, value, raw_data):
        # Save data with callback
        timestamp = raw_data.monitored_item.Value.SourceTimestamp
        self.__data_callback(node.nodeid, value, timestamp)
