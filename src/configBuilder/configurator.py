import json

from sparqlClient import SPARQLClient


class Configurator:
    def __init__(self, connection_params: dict):
        self.__sparql_client = SPARQLClient(connection_params)

    def write_config(self):
        nodes = self.__sparql_client.get_all_nodes()
        with open("../config/opcua_config.json", "w") as file:
            json.dump(nodes, file)

    def on_exit(self):
        self.__sparql_client.disconnect()
