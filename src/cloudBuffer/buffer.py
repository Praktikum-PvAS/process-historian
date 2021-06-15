from typing import Any

from influxdb_client import Point
from .influxWrapper import InfluxWrapper


class Buffer:
    def __init__(self, max_buffer_len: int, connection_params: dict):
        if max_buffer_len < 1:
            raise ValueError("Maximum buffer length must be at least 1!")
        if connection_params is None:
            raise ValueError("Connection parameters must not be None!")
        self.__max_buffer_len = max_buffer_len
        self.__buffer = []
        self.__influx_wrapper = InfluxWrapper(connection_params)

    # TODO very likely not threading safe!
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
        if len(self.__buffer) >= self.__max_buffer_len:
            self.pop_first(1)
        self.__buffer.append(
            Point(node_name).tag("useful", "tag").field("value", value).time(
                timestamp))

    # TODO very likely not threading safe!
    def write_points(self):
        if not len(self.__buffer) == 1:
            status = self.__influx_wrapper.insert(self.__buffer[0])
            if not status:  # successful
                self.__buffer.remove(0)
        elif len(self.__buffer) > 1000:
            __buffer_part = self.__buffer[:1000].copy()
            status = self.__influx_wrapper.insert_many(__buffer_part)
            if not status:  # successful
                self.pop_first(len(__buffer_part))
            else:  # push back when not written
                self.__buffer.insert(0, __buffer_part)
        else:
            status = self.__influx_wrapper.insert_many(self.__buffer)
            if not status:  # successful
                self.pop_first(len(self.__buffer))

    def pop_first(self, number_of_elements: int):
        if number_of_elements < 1:
            raise ValueError("Number of Elements to pop must be at least 1")
        if number_of_elements >= len(self.__buffer):
            raise ValueError("Number of Elements to pop exceeds length of buffer")
        self.__buffer[0:number_of_elements - 1] = []
