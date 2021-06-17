import json
import os
import threading
import time
from pathlib import Path
from typing import Callable, Union

from yaml import safe_load as yaml_load, dump as yaml_dump

from configBuilder import Configurator
from cloudBuffer import Buffer
from opcuaClient import Client as OPCClient


class ProcessHistorian:
    def __init__(self):
        self.__script_location = Path(os.path.dirname(
            os.path.realpath(__file__)))
        self.__config_folder = self.__script_location.parent / "config"
        self.__program_conf_loc = self.__config_folder / "program_config.yaml"
        self.__opcua_conf_loc = self.__config_folder / "opcua_config.json"
        self.__program_conf = {}
        self.__opcua_conf = {}
        self.__exit = False
        self.__work_thread_objs = []
        self.__threads = []

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
                      "exists in the program folder.")
            finally:
                exit(1)

        self.__parse_program_conf()

        # Second step: Config builder to build the OPC UA Config file
        self._config_builder = Configurator(self.__program_conf["tripleStore"],
                                            self.__program_conf["include"],
                                            str(self.__opcua_conf_loc))
        # self._config_builder.write_config()
        self._config_builder.write_debug_config(
            os.path.isfile(self.__opcua_conf_loc))

        # Third step: Check for opcua_config.json and parse it
        self.__parse_opcua_conf()

        # Forth step: Create a buffer for the OPC UA client
        self._buffer = Buffer(self.__program_conf["buffer"]["size"],
                              self.__program_conf["influxdb"])

        # Fifth step: Create the OPC UA client
        self._opcua_client = OPCClient(self.__opcua_conf, self._buffer.append)
        self._opcua_client.connect()

        # Sixth step: Create timed threads to poll the data and
        # subscribe datachange
        intervals = self._opcua_client.get_intervals()
        for interval in intervals:
            # Interval also is the argument for the work function
            poll_obj = self.ProcessHistorianThread(self._opcua_client.poll,
                                                   interval, interval)
            self.__work_thread_objs.append(poll_obj)
            self.__threads.append(threading.Thread(
                name="ProcessHistorian - OPC UA Poll - " + interval + "ms",
                target=poll_obj.work))
        self._opcua_client.subscribe_all()

        # Seventh step: Create timed thread for buffer push
        # No arguments for the push, only write_points
        push_obj = self.ProcessHistorianThread(self._buffer.write_points,
                                               None, 1000)
        self.__work_thread_objs.append(push_obj)
        self.__threads.append(threading.Thread(
            name="ProcessHistorian - CloudBuffer Push",
            target=push_obj.work))

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
        if not os.path.isfile(self.__program_conf_loc):
            print("No program_config.yaml found.")
            try:
                self.__create_empty_program_config()
                print("An empty program configuration " +
                      "was created.")
            except (FileExistsError, PermissionError):
                print("Can't create a empty program configuration. Make " +
                      "sure you have the right permissions and no other " +
                      "folder named \"program_config.yaml\" exists in the " +
                      "config folder.")
            finally:
                exit(1)

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
        elif "size" not in self.__program_conf["buffer"]:
            print("Key \"buffer\" not found in buffer in program config.")
            incorrect = True
        elif not isinstance(self.__program_conf["buffer"]["size"], int):
            print("Value for buffer must be an int! Found " +
                  str(type(self.__program_conf["buffer"]["size"])))
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

        if "host" not in self.__opcua_conf:
            print("Key \"host\" not found in opcua config.")
            print("Your opcua config seems to be incorrect or incomplete.")
            exit()

    def exit(self):

        self.__exit = True
        self._config_builder.on_exit()
        self._opcua_client.unsubscribe_all()
        # Tell all threads they should stop
        for work_obj in self.__work_thread_objs:
            work_obj.should_exit()
        # Wait for them to be really stopped
        for thread in self.__threads:
            thread.join()
        self._opcua_client.disconnect()
        # One last push of the values
        self._buffer.write_points()

    class ProcessHistorianThread:
        def __init__(self, work_function: Callable[[Union[int, None]], None],
                     argument: Union[int, None], interval: int):
            self.__work_function = work_function
            self.__argument = argument
            self.__interval = interval
            self.__sleeps = False
            self.__should_exit = False

        def should_exit(self):
            if self.__sleeps:
                exit()
            else:
                self.__should_exit = True

        def work(self):
            while not self.__should_exit:
                self.__work_function(self.__argument)
                self.__sleeps = True
                if self.__should_exit:
                    exit()
                time.sleep(self.__interval / 1000)  # time.sleep is in seconds
                self.__sleeps = False


if __name__ == "__main__":
    ph = ProcessHistorian()
    waiter = threading.Event()
    try:
        waiter.wait()
    except KeyboardInterrupt:
        ph.exit()
