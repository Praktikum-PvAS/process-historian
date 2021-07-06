#######################################################################################
#    Title: test_opcua_listener source code
#    Author: Valentin Khaydarov
#    Date: 23.01.2021
#    Code version: 511435a
#    Availability: https://github.com/Praktikum-PvAS/planteye-nebula/blob/57616be37af3aee143826c7fca484592c4c27e65/tests/test_opcua_listener.py
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

import pytest
import time
import yaml
import threading
from test_simulation_server import run_simulation_server
from cloudBuffer.buffer import Buffer
from opcuaClient.opcuaClient import Client
from event_logger import log_event


@pytest.fixture()
def my_config():
    cfg = './opcua_config.json'
    return cfg


def test_polling_interval(my_config):
    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    server_thread = threading.Thread(target=run_simulation_server, args=[20])
    server_thread.start()
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(5)
    ua_listener.disconnect()
    time.sleep(5)
    server_thread.join()
    assert 9 <= i <= 11


def connect_online_disconnect_online(my_config):
    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    server_thread = threading.Thread(target=run_simulation_server, args=[30])
    server_thread.start()
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(30)
    ua_listener.disconnect()
    time.sleep(15)
    assert i >= 0


def connect_offline_disconnect_online(my_config):
    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    # my_config['opcua']['number_of_reconnections'] = -1
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(30)
    server_thread = threading.Thread(target=run_simulation_server, args=[15])
    server_thread.start()
    time.sleep(30)
    ua_listener.disconnect()
    time.sleep(15)
    assert i >= 0


def connect_online_disconnect_offline(my_config):
    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    server_thread = threading.Thread(target=run_simulation_server, args=[15])
    server_thread.start()
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(30)
    ua_listener.disconnect()
    time.sleep(15)
    assert i >= 0


def test_reconnection_new_server_unlimited_retries(my_config):
    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    # my_config['opcua']['number_of_reconnections'] = -1
    server_thread = threading.Thread(target=run_simulation_server, args=[20])
    server_thread.start()
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(60)
    server_thread.join()
    iterator_after_first_stop = i
    log_event(my_config, 'TEST', '', 'INFO', 'iter = ' + str(i))
    server_thread = threading.Thread(target=run_simulation_server, args=[20])
    server_thread.start()
    time.sleep(20)
    ua_listener.disconnect()
    time.sleep(15)
    log_event(my_config, 'TEST', '', 'INFO', 'iter = ' + str(i))
    server_thread.join()
    assert i > iterator_after_first_stop


def test_continuous_reading(my_config):
    # TODO
    #my_config['opcua']['number_of_reconnections'] = -1

    i = 0

    def callback(a, b, c, d):
        nonlocal i
        i += 1

    server_thread = threading.Thread(target=run_simulation_server, args=[20])
    server_thread.start()
    ua_listener = Client(my_config, callback)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(10)
    ua_listener.disconnect()
    server_thread.join()
    time.sleep(5)

    """
    # TODO adapt code
    list_of_metrics = [metric['metric_id'] for metric in my_config['metrics']]
    metric_values = [[] for _ in range(len(list_of_metrics))]

    for buffer_entity in my_buffer.buffer:
        metric_idx = list_of_metrics.index(buffer_entity.data['node'].metric_id)
        metric_values[metric_idx].append(buffer_entity.data['data_variant'].Value.Value)

    increments_equal_one = True
    for metric_value_set in metric_values:
        for i in range(1, len(metric_value_set), 1):
            if metric_value_set[i] != metric_value_set[i - 1] + 1:
                increments_equal_one = False
                break
    assert increments_equal_one == True
    """
    intervall = 1000
    storage = Client.poll(intervall)
    assert False


# TODO: check if test is necessary
def test_continous_reading_negative_case(my_config):
    my_config['opcua']['number_of_reconnections'] = -1
    my_config['metrics'][0]['interval'] = 500

    server_thread = threading.Thread(target=run_simulation_server, args=[20])
    server_thread.start()
    my_buffer = Buffer(my_config)
    ua_listener = Client(my_config, my_buffer)
    time.sleep(3)
    ua_listener.connect()
    time.sleep(10)
    ua_listener.exit()
    server_thread.join()
    time.sleep(5)

    list_of_metrics = [metric['metric_id'] for metric in my_config['metrics']]
    metric_values = [[] for _ in range(len(list_of_metrics))]

    for buffer_entity in my_buffer.buffer:
        metric_idx = list_of_metrics.index(buffer_entity.data['node'].metric_id)
        metric_values[metric_idx].append(buffer_entity.data['data_variant'].Value.Value)

    increments_equal_one = True
    for metric_value_set in metric_values:
        for i in range(1, len(metric_value_set), 1):
            if metric_value_set[i] != metric_value_set[i - 1] + 1:
                increments_equal_one = False
                break
    assert increments_equal_one == False
