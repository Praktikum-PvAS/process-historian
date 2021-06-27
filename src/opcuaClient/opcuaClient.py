import opcua
from datetime import datetime
from opcua.ua.attribute_ids import AttributeIds
from typing import Any, Callable, List, Tuple, Dict


class CustomNode:
    def __init__(self, assembly_type: str, assembly_identifier: str,
                 attribute_name: str,
                 opc_node: opcua.Node):
        self.assembly_type = assembly_type
        self.assembly_identifier = assembly_identifier
        self.attribute_name = attribute_name
        self.node_obj = opc_node


class Client:
    def __init__(self, opcua_config: dict,
                 callback: Callable[[str, List[Tuple[str, str]], Any, Any],
                                    None]):
        if opcua_config is None:
            ValueError("opcua_config must not be None")
        if not callable(callback):
            ValueError("callback is not callable")

        self.__opcua_config = opcua_config
        self.__url = self.__opcua_config["host"]
        self._opcua_lib_client = opcua.Client(self.__url)
        self.__callback = callback
        self._nodes2poll = {}  # dictionary with [interval] = list<nodes>
        self._nodes2sub = {}
        self.__subscription_handles = []
        self.__namespace_adapter = {}

        self.__init_lists()

        self.__subscription = None
        self.__subHandler = self.SubscriptionHandler(callback, self._nodes2sub)

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
        self.__get_namespace_indexes()

        # get every node from config
        type_list = ["sensors", "actuators", "services"]
        for node_type in type_list:
            # search for every node of that type
            for i in range(len(self.__opcua_config[node_type])):
                nodes_attributes = \
                    self.__opcua_config[node_type][i]["attributes"]
                for attribute in nodes_attributes:
                    # add nodeId to the list
                    if attribute["mode"] == "poll":
                        # get interval and node
                        interval = attribute["interval"]
                        # create a opcua node object
                        node_obj = self._opcua_lib_client.get_node(
                            self.__create_node_id(attribute["namespace"],
                                                  attribute["node_identifier"]))
                        # create a CustomNode to store more information
                        node = CustomNode(node_type, self.__opcua_config[node_type][i]["id"],
                                          attribute["name"], node_obj)
                        # append the node and interval to the list in the
                        # dictionary
                        temp_list = self._nodes2poll.get(interval, [])
                        temp_list.append(node)
                        # store the list in the dict
                        self._nodes2poll[interval] = temp_list
                    elif attribute["mode"] == "subscription":
                        node_obj = self._opcua_lib_client.get_node(
                            self.__create_node_id(attribute["namespace"],
                                                  attribute["node_identifier"]))
                        node = CustomNode(node_type, self.__opcua_config[node_type][i]["id"],
                                          attribute["name"], node_obj)
                        self._nodes2poll[node_obj] = node

    def __get_namespace_indexes(self):
        namespaces = self.__get_all_namespaces()
        ns_array = self._opcua_lib_client.get_namespace_array()
        for ns in namespaces:
            self.__namespace_adapter[ns] = ns_array.index(ns)

    def __get_all_namespaces(self):
        namespaces = []

        type_list = ["sensors", "actuators", "services"]
        for node_type in type_list:
            # search for every node of that type
            for i in range(len(self.__opcua_config[node_type])):
                nodes_attributes = \
                    self.__opcua_config[node_type][i]["attributes"]
                for attribute in nodes_attributes:
                    if attribute["namespace"] not in namespaces:
                        namespaces.append(attribute["namespace"])

        return namespaces

    def __create_node_id(self, namespace, identifier):
        return f"ns={self.__namespace_adapter[namespace]};{identifier}"

    def get_intervals(self):
        # return all existing polling intervals from the polling dictionary
        return self._nodes2poll.keys()

    def poll(self, interval: int):
        nodes = self._nodes2poll[interval]
        # get node ids
        nodeids = [custom_node.node_obj.nodeid for custom_node in nodes]

        results = self._opcua_lib_client.uaclient \
            .get_attributes(nodeids, AttributeIds.Value)

        for result in results:
            if result.SourceTimestamp is None:
                result.SourceTimestamp = datetime.now().isoformat()

        # returns the value to a callback function
        for i in range(len(results)):
            self.__callback(nodes[i].assembly_identifier,  # measurement
                            [("assembly_type", nodes[i].assembly_type)],  # tags
                            [(nodes[i].attribute_name, results[i].Value.Value)],  # values
                            results[i].SourceTimestamp)

    def poll_server_status(self):
        node = self._opcua_lib_client.get_node("ns=0;i=2259")
        return node.get_value()

    def subscribe_all(self):
        # create one subscription and let subHandler watch it
        self.__subscription = self._opcua_lib_client \
            .create_subscription(100, self.__subHandler)
        # subscribe to node
        if self._nodes2sub:
            handles = self.__subscription.subscribe_data_change(self._nodes2sub)
            self.__subscription_handles = handles

    def unsubscribe_all(self):
        if self.__subscription_handles:
            self.__subscription.unsubscribe(self.__subscription_handles)

    class SubscriptionHandler:
        def __init__(self, data_callback: Callable[
            [str, List[Tuple[str, str]], Any, Any], None],
                     node_dict: Dict[opcua.Node, CustomNode]):
            self.__data_callback = data_callback
            self.__node_dict = node_dict

        def datachange_notification(self, node: opcua.Node, value, raw_data):
            # Save data with callback
            timestamp = raw_data.monitored_item.Value.SourceTimestamp
            c_node = self.__node_dict[node]
            self.__data_callback(c_node.assembly_identifier,  # measurement
                                 [("assembly_type", c_node.assembly_type)],  # tags
                                 [(c_node.attribute_name, value)],  # values
                                 timestamp)
