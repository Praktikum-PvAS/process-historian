from opcua import Node


class CustomNode:
    """
    Node object to store node information
    """

    def __init__(self, assembly_type: str, assembly_identifier: str,
                 attribute_name: str,
                 opc_node: Node):
        """
        Constructor
        :param assembly_type: Type of the DataAssembly the node belongs to.
        Possible values are "sensors", "actuators" and "services".
        :param assembly_identifier: Identifier of the DataAssembly
        :param attribute_name: Name of the Attribute of the DataAssembly
        :param opc_node: Node object from the opcua library
        """

        type_list = ["sensors", "actuators", "services"]
        if not (assembly_type in type_list):
            raise ValueError("Unexpected assembly type. Expected are only "
                             "sensors, actuators or services!")

        self.assembly_type = assembly_type
        self.assembly_identifier = assembly_identifier
        self.attribute_name = attribute_name
        self.node_obj = opc_node
