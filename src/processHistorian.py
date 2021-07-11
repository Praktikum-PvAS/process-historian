import json
import os
import threading
import time
from pathlib import Path
from typing import Callable, Union
import argparse

from yaml import safe_load as yaml_load, dump as yaml_dump
from jsonschema import validate, ValidationError

from configBuilder import Configurator
from cloudBuffer import Buffer
from opcuaClient import Client as OPCClient


class ProcessHistorian:
    """
    Main class. Connects the configBuilder, opcuaClient and cloudBuffer
    packages.
    """

    def __init__(self):
        """
        Constructor

        The constructor sets up everything so the program will work. It does
        that with the following steps:

        1. Check the program configuration and parse it.
        2. Create a config builder and fetch the data from the TripleStore.
        2.5 Delete the config builder.
        3. Check and parse the config written by the config builder.
        4. Create a buffer.
        5. Create a OPC UA client and connect it.
        6. Create all necessary work threads for polling.
        7. Create a thread for pushing the data from buffer to the InfluxDB
        8. Start all the threads and subscribe to necessary nodes on the OPC UA Server.
        """
        self.__script_location = Path(os.path.dirname(
            os.path.realpath(__file__)))
        self.__config_folder = self.__script_location.parent / "config"
        self.__program_conf_loc = self.__config_folder / "program_config.yaml"
        self.__opcua_conf_loc = self.__config_folder / "opcua_config.json"
        self.__schemata_loc = self.__script_location / "json_schemata"
        self.__program_conf = {}
        self.__opcua_conf = {}
        self.__push_thread_obj = None
        self.__push_thread = None
        self.__opc_thread_objs = []
        self.__opc_threads = []

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

        # After that we can delete the config builder
        del self._config_builder

        # Third step: Check for opcua_config.json and parse it
        self.__parse_opcua_conf()

        # Forth step: Create a buffer for the OPC UA client
        self._buffer = Buffer(self.__program_conf["buffer"]["size"],
                              self.__program_conf["influxdb"])

        # Fifth step: Create the OPC UA client
        self._opcua_client = OPCClient(self.__opcua_conf,
                                       self._buffer.append,
                                       self._buffer.append_many)
        self.wait_for_new_opc_connection()

        # Sixth step: Create timed threads to poll the data and
        # subscribe datachange
        intervals = self._opcua_client.get_intervals()
        for interval in intervals:
            # Interval also is the argument for the work function
            poll_obj = self.ProcessHistorianThread(self._opcua_client.poll,
                                                   interval, interval)
            self.__opc_thread_objs.append(poll_obj)
            self.__opc_threads.append(threading.Thread(
                name=f"ProcessHistorian - OPC UA Poll - {interval}ms",
                target=poll_obj.work))

        # Eighth step: Subscribe and start all threads
        for thread in self.__opc_threads:
            thread.start()
        self._opcua_client.subscribe_all()

        # Seventh step: Create timed thread for buffer push
        # No arguments for the push, only write_points
        self.__push_thread_obj = self.ProcessHistorianThread(self._buffer.write_points,
                                                             None,
                                                             self.__buffer_push_interval)
        self.__push_thread = threading.Thread(
            name="ProcessHistorian - CloudBuffer Push",
            target=self.__push_thread_obj.work)
        self.__push_thread.start()

    def wait_for_new_opc_connection(self):
        """
        Helper function that waits for the OPC UA
        """
        self._opcua_client.disconnect(log=False)
        print("Waiting for opc connection to be (re)established...")
        while True:
            try:
                time.sleep(self.heartbeat_interval_seconds)
                self.opc_defibrillator()
                break
            except KeyboardInterrupt:
                self.exit()
                exit()
            except:
                pass

    def listen_for_opc_heartbeat(self):
        """
        Heartbeat function to check if the OPC UA Client is still alive.
        :raise: Any error if not alive because the opcua library raises
        different errors.
        """
        if self._opcua_client.poll_server_status() != 0:
            raise ConnectionError("No heartbeat!")

    def opc_defibrillator(self):
        """
        Reconnects the OPC UA Client
        :raise: Any error if server is not available because the opcua library
        raises different errors.
        """
        self._opcua_client.connect()
        self.listen_for_opc_heartbeat()

    def resubscribe_opc(self):
        """
        Resubscribes to opc nodes.
        """
        self._opcua_client.subscribe_all()

    def __create_empty_program_config(self):
        """
        Creates an empty config with a few default values.
        """
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
                    "size": 1000000,
                    "push_interval": 1000
                },
                "__heartbeat_interval": 1000
            }, prog_conf)

    def __parse_program_conf(self):
        """
        Parses the program configuration. Also checks if it uses the correct
        JSON schema.
        """
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

        self.__schemata_loc = self.__script_location / "json_schemata"
        program_schema = self.__schemata_loc / "program_config_schema.json"

        try:
            with open(program_schema) as fschema:
                schema = json.load(fschema)
        except (FileExistsError, PermissionError):
            print("Can't read json validation schema for program_config! " +
                  "Make sure you have the " +
                  "right permissions and the file exists")
            print("Config check is skipped.")
            return
        except json.JSONDecodeError:
            print("JSON validation schema for program config is incorrect.")
            print("Config check is skipped.")
            return

        try:
            validate(self.__program_conf, schema)
            self.__heartbeat_interval = self.__program_conf.get(
                "__heartbeat_interval",
                1000)
            self.__buffer_push_interval = self.__program_conf["buffer"] \
                .get("push_interval", 1000)
        except ValidationError as e:
            print("Your program config seems to be incorrect or incomplete.")
            print("The reason is below:")
            print()
            print(e)
            exit()

    def __parse_opcua_conf(self):
        """
        Parses the OPC UA configuration. Also checks if it uses the correct
        JSON schema.
        """
        try:
            with open(self.__opcua_conf_loc, "r") as opcua_conf:
                self.__opcua_conf = json.load(opcua_conf)
        except (FileExistsError, PermissionError):
            print("Can't read opcua config! Make sure you have the " +
                  "right permissions and the file exists")
            exit()

        opcua_schema = self.__schemata_loc / "opcua_config_schema.json"
        try:
            with open(opcua_schema) as fschema:
                schema = json.load(fschema)
        except (FileExistsError, PermissionError):
            print("Can't read json validation schema for opcua_config! " +
                  "Make sure you have the " +
                  "right permissions and the file exists")
            print("Config check is skipped.")
            return
        except json.JSONDecodeError:
            print("JSON validation schema for opcua config is incorrect.")
            print("Config check is skipped.")
            return

        try:
            validate(self.__opcua_conf, schema)
        except ValidationError as e:
            print("Your program config seems to be incorrect or incomplete.")
            print("The reason is below:")
            print()
            print(e)
            exit()

    def exit(self):
        """
        Safely disconnect all connections and terminate all threads in the
        correct order and push the last values in buffer so no data is lost.
        """
        print("Exiting the ProcessHistorian...")
        print("Waiting for all worker threads to finish...")
        # Tell all threads they should stop
        if self.__push_thread_obj:
            self.__push_thread_obj.should_exit()
        for work_obj in self.__opc_thread_objs:
            work_obj.should_exit()
        # Wait for them to be really stopped
        if self.__push_thread:
            self.__push_thread.join()
        for thread in self.__opc_threads:
            thread.join()
        print("Disconnecting from OPC UA Server...")
        self._opcua_client.unsubscribe_all()
        self._opcua_client.disconnect()
        # One last push of the values
        print("Push remaining values (if any) from buffer...")
        status = self._buffer.write_points()
        while status:
            print("Buffer cannot be sent.")
            choice = input("Try again?  (Y/n): ")
            while choice.lower() != "n" and \
                    choice.lower() != "y" and \
                    choice != "":
                choice = input("Invalid input! " +
                               "Try to push buffer again? (Y/n): ")
            if choice.lower() == "n":
                break
            status = self._buffer.write_points()
        print("Exit complete! Goodbye!")
        exit()

    @property
    def heartbeat_interval_seconds(self):
        return self.__heartbeat_interval / 1000

    class ProcessHistorianThread:
        """
        Object used as context in a background thread. Has the ability to call
        jobs in intervals and also to exit only when not currently working so
        network communication won't be ended abruptly.
        """

        def __init__(self, work_function: Callable[[Union[int, None]], None],
                     argument: Union[int, None], interval: int):
            """
            Constructor
            :param work_function: Function that will be called in intervals
            :param argument: Argument for the work_function
            :param interval: Interval in milliseconds in which the
            work_function will be called
            """
            self.__work_function = work_function
            self.__argument = argument
            self.__interval = interval
            self.__should_exit = threading.Event()
            self.__should_exit.clear()

        def should_exit(self):
            """
            Sets the exit flag. If the thread currently is sleeping (idle) it
            will be halted immediately.
            """
            self.__should_exit.set()

        def work(self):
            """
            Actual function that will run in another thread. It will loop and
            call the work_function in the specified interval.
            """
            while not self.__should_exit.is_set():
                if self.__argument:
                    self.__work_function(self.__argument)
                else:
                    self.__work_function()

                # Uses the timeout instead of wait
                self.__should_exit.wait(self.__interval / 1000)  # in seconds


if __name__ == "__main__":
    """
    Main function
    Creates the ProcessHistorian and checks with the heartbeat function if the
    connection to the OPC UA server is still alive.
    """
    parser = argparse.ArgumentParser(description="Finds relevant opc ua nodes using Triplestore " +
                                                 "and archives their values in an InfluxDB")
    parser.add_argument('-f', '--faststart', help="start Process Historian without generating a new config for opc ua",
                        action='store_true')
    parser.add_argument('--reset-intervals', help="""reset poll intervals for known objects on opc ua config
                                                     generation to the configured value""",
                        action='store_true')
    parser.add_argument('--default-opc-mode', choices=["subscribe", "poll"], help="""when adding a node to opc ua config
                                                                                    default to subscription or polling
                                                                                    """)
    parser.add_argument('--reset-opc-mode', action='store_true', help="""reset opc ua modes for known objects 
                                                    on opc ua config generation to polling with configured interval.
                                                    May be used with --default-opc-mode to reset to subscriptions""", )
    parser.add_argument('-n', '--new-config', help="force generation of a new sample program config",
                        action='store_true')
    parser.add_argument('--silent-exit-mode', choices=["retry", "exit"], help="""if the buffer can't be sent to the
                                        InfluxDB on exit, don't ask but either retry every push interval or exit""")
    args = parser.parse_args()

    if args.reset_intervals:
        print("Warning: The opc ua config builder is not yet implemented! --reset-intervals does not work.")
    if args.default_opc_mode:
        print("Warning: The opc ua config builder is not yet implemented! --default-opc-mode does not work.")
    if args.reset_opc_mode:
        print("Warning: The opc ua config builder is not yet implemented! --reset-opc-mode does not work.")

    if not args.faststart:
        print("Warning: The opc ua config builder is not yet implemented! --faststart is implied.")

    ph = ProcessHistorian()
    hb_interval = ph.heartbeat_interval_seconds  # in seconds for time.sleep()

    while True:
        try:
            while True:
                ph.listen_for_opc_heartbeat()
                time.sleep(hb_interval)
        except KeyboardInterrupt:
            ph.exit()
            exit()
        except:
            ph.wait_for_new_opc_connection()
            print("Resubscribing to opc...")
            ph.resubscribe_opc()
