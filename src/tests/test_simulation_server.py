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


import yaml
import time
import threading
from opcua import Server
from event_logger import log_event


def run_simulation_server(steps):
    """
    This support function creates a simple OPC UA server with node listed in the config file
    :param steps: Lifecycle of the server
    :return:
    """

    with open('config_test.yml') as config_file:
        cfg = yaml.safe_load(config_file)

    # setup the server
    server = Server()
    server.set_endpoint(cfg['opcua']['url'])

    # setup the namespace
    uri = "http://examples.freeopcua.github.io"
    idx = server.register_namespace(uri)

    # get objects node
    objects = server.get_objects_node()

    # server start
    server.start()
    log_event(cfg, 'OPCUA TEST SERVER', '', 'INFO', 'OPC UA server started')

    # populating the address space
    myobj = objects.add_object(idx, "TestDataAssembly")

    nodes = []
    metrics = cfg['metrics']
    for metric in metrics:
        metric_id = metric['metric_id']
        meas = metric['measurement']
        tag = metric['tagname']
        var = metric['variable']
        ns = metric['nodeNamespace']
        id = metric['nodeId']
        method = metric['method']
        time_interval = metric['interval']
        node_str = 'ns=' + str(ns) + '; i=' + str(id)
        nodes.append(myobj.add_variable(node_str, var, -1))

    # update variable
    time.sleep(1)
    for it in range(steps):
        for node in nodes:
            node.set_value(node.get_value() + 1)
            time.sleep(0.5)
    time.sleep(2)
    server.stop()
    log_event(cfg, 'OPCUA TEST SERVER', '', 'INFO', 'OPC UA server stopped')


if __name__ == '__main__':
    run_simulation_server(3600)
