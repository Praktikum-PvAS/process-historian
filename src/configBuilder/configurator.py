import json

from .sparqlClient import SPARQLClient


class Configurator:
    """
    Configures the connection to the TripleStore and writes the
    OPC UA config
    """

    def __init__(self, connection_params: dict, included_types: list,
                 config_loc: str):
        """
        Constructor
        :param connection_params: Connection params for the SPARQLClient
        :param included_types: List of included DataAssembly types
        :param config_loc: Path where the OPC UA config should be written to
        """
        self.__config_loc = config_loc
        self.__sparql_client = SPARQLClient(connection_params, included_types)

    def write_config(self):
        """
        Fetches the data from TripleStore and writes the config
        """
        nodes = self.__sparql_client.get_all_nodes()
        with open(self.__config_loc, "w") as file:
            json.dump(nodes, file, indent=2)

    def write_debug_config(self, exists: bool):
        """
        Writes a debug config if no other config is already in place.
        :param exists: Config already exists
        """
        if exists:
            return
        else:
            with open(self.__config_loc, "w") as file:
                json.dump({
                    "host": "http://example.com",
                    "actuators": [],
                    "sensors": [],
                    "services": []
                }, file, indent=2)

    def on_exit(self):
        """
        Disconnects the SPARQLClient
        """
        self.__sparql_client.disconnect()
