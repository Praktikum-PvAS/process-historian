from typing import Any

from influxdb_client import Point
from .influxWrapper import InfluxWrapper

import threading


class Buffer:
    def __init__(self, max_buffer_len: int, connection_params: dict):
        if max_buffer_len < 1:
            raise ValueError("Maximum buffer length must be at least 1!")
        if connection_params is None:
            raise ValueError("Connection parameters must not be None!")
        self.__max_buffer_len = max_buffer_len
        self.__buffer = []
        self.__influx_wrapper = InfluxWrapper(connection_params)
        self.__sem = threading.Semaphore()

    def append(self, node_name: str, value: Any, timestamp: Any):
        if node_name is None:
            raise ValueError("node name MUST NOT be None!")
        if node_name == "":
            raise ValueError("node name MUST NOT be empty!")
        if value is None:
            raise ValueError("value MUST NOT be None!")
        if timestamp is None:
            raise ValueError("Timestamp MUST NOT be None!")
        # TODO add better tags
        self.__sem.acquire()
        if len(self.__buffer) >= self.__max_buffer_len:
            self.pop_first(1)
        self.__buffer.append(
            Point(node_name).tag("useful", "tag").field("value", value).time(
                timestamp))
        self.__sem.release()

    def write_points(self):
        self.__sem.acquire()
        if len(self.__buffer) > 1000:
            buffer_part = self.__buffer[:1000].copy()
            status = self.__influx_wrapper.insert_many(buffer_part)
            if not status:  # successful
                self.pop_first(len(buffer_part))
            else:  # push back when not written
                self.__buffer.insert(0, buffer_part)
        else:
            buffer_copy = self.__buffer.copy()
            status = self.__influx_wrapper.insert_many(buffer_copy)
            if not status:  # successful
                self.pop_first(len(buffer_copy))
        self.__sem.release()

    def pop_first(self, number_of_elements: int):
        if number_of_elements < 1:
            raise ValueError("Number of Elements to pop must be at least 1")
        if number_of_elements >= len(self.__buffer):
            raise ValueError("Number of Elements to pop exceeds length of buffer")
        self.__buffer[0:number_of_elements - 1] = []
