import json
import os
from yaml import safe_load as yaml_load, dump as yaml_dump

from configBuilder import Configurator
# TODO
# fill __init__.py of cloud_buffer so import work
# from cloudBuffer import Buffer
from opcuaClient import Client as OPCClient


class ProcessHistorian:
    def __init__(self):
        self.__script_location = os.path.dirname(os.path.realpath(__file__))
        self.__config_folder = self.__script_location + "/../config"
        self.__program_conf_loc = self.__config_folder + "/program_config.yaml"
        self.__opcua_conf_loc = self.__config_folder + "/opcua_config.json"
        self.__program_conf = {}
        self.__opcua_conf = {}

        # First step: Make sure the program config is correct and parse it
        if not os.path.isdir(self.__config_folder):
            print("The config folder wasn't found.")
            try:
                os.mkdir(self.__config_folder)
                self.__create_empty_program_config()
                print("A config folder with an empty program configuration " +
                      "was created.")
            except (FileExistsError, PermissionError):
                print("Can't create a config folder. Make sure you have the " +
                      "right permissions and no other file named \"config\" " +
                      "in the program folder.")
            finally:
                exit(1)

        self.__parse_program_conf()

        # Second step: Config builder to build the OPC UA Config file
        # TODO
        # "include" and the location of the opcua_configuration as attributes
        self._config_builder = Configurator(self.__program_conf["tripleStore"])
        self._config_builder.write_config()

        # Third step: Check for opcua_config.json and parse it
        self.__parse_opcua_conf()

        # Forth step: Create a buffer for the OPC UA client
        # TODO
        # fill __init__.py of cloud_buffer so import work
        # self._buffer = Buffer()

        # Fifth step: Create the OPC UA client
        # TODO
        # wait for buffer
        # self._opcua_client = OPCClient(self.__opcua_conf, self._buffer.append)
        # self._opcua_client.connect()

        # Sixth step: Create timed threads to poll the data and
        # subscribe datachange
        # TODO
        # Threads
        # self._opcua_client.subscribe_all()

    def __create_empty_program_config(self):
        with open(self.__program_conf_loc, "w") as prog_conf:
            yaml_dump({
                "include": [
                    "sensors", "actuators", "services"
                ],
                "tripleStore": {
                    "host": "http://example.com",
                    "username": "",
                    "password": ""
                },
                "influxdb": {
                    "host": "http://example.com",
                    "token": "",
                    "organization": "",
                    "bucket": ""
                },
                "buffer": {
                    "size": 1000000
                }
            }, prog_conf)

    def __parse_program_conf(self):
        try:
            with open(self.__program_conf_loc) as prog_conf:
                self.__program_conf = yaml_load(prog_conf)
        except (FileExistsError, PermissionError):
            print("Can't read program_config! Make sure you have the " +
                  "right permissions and the file exists")
            exit()

        incorrect = False

        if "buffer" not in self.__program_conf:
            print("Key \"buffer\" not found in program config.")
            incorrect = True
        elif not isinstance(self.__program_conf["buffer"], int):
            print("Value for buffer must be an int!")
            incorrect = True
        if "include" not in self.__program_conf:
            print("Key \"include\" not found in program config.")
            incorrect = True
        if "influxdb" not in self.__program_conf:
            print("Key \"influxdb\" not found in program config.")
            incorrect = True
        if "tripleStore" not in self.__program_conf:
            print("Key \"tripleStore\" not found in program config.")
            incorrect = True

        if incorrect:
            print("Your program config seems to be incorrect or incomplete.")
            exit()

    def __parse_opcua_conf(self):
        try:
            with open(self.__opcua_conf_loc, "r") as opcua_conf:
                self.__opcua_conf = json.load(opcua_conf)
        except (FileExistsError, PermissionError):
            print("Can't read opcua config! Make sure you have the " +
                  "right permissions and the file exists")
            exit()

        if "host" not in opcua_conf:
            print("Key \"host\" not found in opcua config.")
            print("Your opcua config seems to be incorrect or incomplete.")
            exit()


if __name__ == "__main__":
    ProcessHistorian()
