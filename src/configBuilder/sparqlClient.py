from typing import Dict, List

from SPARQLWrapper import SPARQLWrapper


class SPARQLClient:
    """
    Client to make SPARQL requests to the TripleStore
    """

    def __init__(self, connection_params: Dict, included_types: List):
        """
        Constructor
        :param connection_params: Connection params to the TripleStore
        :param included_types: List of included DataAssembly types
        """
        if connection_params is None:
            raise ValueError("connection_params must not be None")
        if "host" not in connection_params \
                or connection_params["host"] is None \
                or connection_params["host"] == "":
            raise ValueError("No valid URL provided")
        """if "username" not in connection_params \
                or connection_params["username"] is None \
                or connection_params["username"] == "":
            raise ValueError("No valid username provided")
        if "password" not in connection_params \
                or connection_params["password"] is None \
                or connection_params["password"] == "":
            raise ValueError("No valid password provided")"""

        self.__connection_params = connection_params
        self.__included_types = included_types
        self.__sparql = SPARQLWrapper(connection_params["host"])

    def connect(self):
        """
        Currently does nothing. Should connect the client to the TripleStore.
        """
        # TODO
        pass

    def disconnect(self):
        """
        Currently does nothing. Should disconnect from the TripleStore.
        """
        # TODO
        pass

    def get_all_nodes(self) -> Dict:
        """
        Currently does nothing. Should fetch all necessary data from the
        TripleStore and make an organized dict out of it.
        :return: Dict in schema of the opcua_config_schema.json
        """
        # TODO
        # - find opc ua host
        # - find sensors, actuators, services (depends on "included_types")
        # - for all find attributes
        # - from attributes get nodeId and namespace
        # - return dict
        pass
