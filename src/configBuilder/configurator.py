import json

from .sparqlClient import SPARQLClient


class Configurator:
    def __init__(self, connection_params: dict, included_types: list,
                 config_loc: str):
        self.__config_loc = config_loc
        self.__sparql_client = SPARQLClient(connection_params, included_types)

    def write_config(self):
        nodes = self.__sparql_client.get_all_nodes()
        with open(self.__config_loc, "w") as file:
            json.dump(nodes, file)

    def write_debug_config(self, exists: bool):
        if exists:
            return
        else:
            with open(self.__config_loc, "w") as file:
                json.dump({
                    "host": "http://example.com",
                    "actuators": [],
                    "sensors": [],
                    "services": []
                }, file)

    def on_exit(self):
        self.__sparql_client.disconnect()
