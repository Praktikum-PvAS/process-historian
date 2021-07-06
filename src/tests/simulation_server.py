#######################################################################################
#    Title: opcua_simultion_server source code
#    Author: Valentin Khaydarov
#    Date: 23.01.2021
#    Code version: 511435a
#    Availability: https://github.com/Praktikum-PvAS/planteye-nebula/blob/57616be37af3aee143826c7fca484592c4c27e65/src_test/opcua_simultion_server.py
#
#    MIT License
#
#    Copyright (c) 2021 Valentin Khaydarov
#    Copyright (c) 2021 Max Kirchner, Patrick Suwinski
#
#    Permission is hereby granted, free of charge, to any person obtaining a copy
#    of this software and associated documentation files (the "Software"), to deal
#    in the Software without restriction, including without limitation the rights
#    to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
#    copies of the Software, and to permit persons to whom the Software is
#    furnished to do so, subject to the following conditions:
#
#    The above copyright notice and this permission notice shall be included in all
#    copies or substantial portions of the Software.
#
#    THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#    IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#    FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#    AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#    LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
#    OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
#    SOFTWARE.
#######################################################################################
import json
import time
import logging
from random import random
from threading import Event
from opcua import Server


def run_simulation_server(steps: int, ready_event: Event):
    """
    This support function creates a simple OPC UA server with node listed in
    the config file
    :param steps: Lifecycle of the server
    :param ready_event: threading.Event that fires when the server is ready
    """

    with open("opcua_config.json") as config_file:
        cfg = json.load(config_file)

    # setup the server
    server = Server()
    server.set_endpoint(cfg["host"])

    # setup the namespace
    ns_uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(ns_uri)

    # get objects node
    objects = server.get_objects_node()

    # server start
    server.start()

    logging.log(logging.DEBUG, "OPC UA simulation server started")

    # populating the address space
    my_obj = objects.add_object(idx, "TestDataAssembly")

    nodes = []
    for at in ["sensors", "actuators", "services"]:
        for assembly in range(len(cfg[at])):
            for attr in range(len(cfg[at][assembly]["attributes"])):
                name = cfg[at][assembly]["attributes"][attr]["name"]
                ns = idx
                nid = cfg[at][assembly]["attributes"][attr]["node_identifier"]
                nid_string = f"ns={ns};{nid}"
                nodes.append(my_obj.add_variable(nid_string, name, -1))

    ready_event.set()
    # update variable
    time.sleep(0.1)
    for it in range(steps):
        for node in nodes:
            node.set_value(it)
        time.sleep(1)
    time.sleep(0.5)
    server.stop()
    logging.log(logging.DEBUG, "OPC UA Simulation server stopped")


if __name__ == "__main__":
    run_simulation_server(3600, Event())
