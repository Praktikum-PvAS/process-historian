import sparql


class SPARQLClient:
    def __init__(self, connection_params: dict):
        self.connection_params = connection_params
        self.connect(connection_params)

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
