import sparql


class SPARQLClient:
    def __init__(self, connection_params: dict):
        if connection_params is None:
            raise ValueError("connection_params must not be None")
        if "url" not in connection_params or connection_params["url"] is None \
                or connection_params["url"] == "":
            raise ValueError("No valid URL provided")
        if "username" not in connection_params \
                or connection_params["username"] is None \
                or connection_params["username"] == "":
            raise ValueError("No valid username provided")
        if "password" not in connection_params \
                or connection_params["password"] is None \
                or connection_params["password"] == "":
            raise ValueError("No valid password provided")

        self.connection_params = connection_params
        self.sparql = sparql.Service(connection_params["url"])

    def connect(self, connection_params):
        # TODO
        pass

    def disconnect(self):
        # TODO
        pass

    def get_all_nodes(self):
        # TODO
        # - find opc ua host
        # - find sensors, actuators, services
        # - for all find attributes
        # - from attributes get nodeId and namespace
        # - return dict
        pass
