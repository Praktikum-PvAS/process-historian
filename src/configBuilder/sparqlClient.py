from SPARQLWrapper import SPARQLWrapper


class SPARQLClient:
    def __init__(self, connection_params: dict, included_types: list):
        if connection_params is None:
            raise ValueError("connection_params must not be None")
        if "host" not in connection_params \
                or connection_params["host"] is None \
                or connection_params["host"] == "":
            raise ValueError("No valid URL provided")
        if "username" not in connection_params \
                or connection_params["username"] is None \
                or connection_params["username"] == "":
            raise ValueError("No valid username provided")
        if "password" not in connection_params \
                or connection_params["password"] is None \
                or connection_params["password"] == "":
            raise ValueError("No valid password provided")

        self.__connection_params = connection_params
        self.__included_types = included_types
        self.__sparql = SPARQLWrapper(connection_params["host"])

    def connect(self, connection_params):
        # TODO
        pass

    def disconnect(self):
        # TODO
        pass

    def get_all_nodes(self):
        # TODO
        # - find opc ua host
        # - find sensors, actuators, services (depends on "included_types")
        # - for all find attributes
        # - from attributes get nodeId and namespace
        # - return dict
        pass
