from typing import Any, List, Tuple, Union

from influxdb_client import Point
from .influxWrapper import InfluxWrapper

import threading


class Buffer:
    """
    A buffer that stores data points and writes those to a InfluxDB.
    """

    def __init__(self, max_buffer_len: int, connection_params: dict):
        """
        Constructor of the class.
        :param max_buffer_len: Maximum amount of points which can be stored in
        the buffer
        :param connection_params: Necessary connection parameters to connect to
        the InfluxDB.
        """
        if max_buffer_len < 1:
            raise ValueError("Maximum buffer length must be at least 1!")
        if connection_params is None:
            raise ValueError("Connection parameters must not be None!")
        self.__max_buffer_len = max_buffer_len
        self.__buffer = []
        self.__influx_wrapper = InfluxWrapper(connection_params)
        self.__sem = threading.Semaphore()

    def append(self, measurement: str,
               tags: Union[List[Tuple[str, str]], None],
               values: Union[List[Tuple[str, Any]], None],
               timestamp: Any):
        """"
        Function which adds a measurement point at the end of the private list
        buffer.
        :param measurement: Kind of measurement.
        :param tags: List of tuples, each containing tag and tag value
        :param values: List of tuples, each containing value name and measured
        value
        :param timestamp: Timestamp of the measurement
        """
        if measurement is None:
            raise ValueError("measurement MUST NOT be None!")
        if measurement == "":
            raise ValueError("measurement MUST NOT be empty!")
        if tags is None:
            tags = []
        if values is None or values == []:
            raise ValueError("value MUST NOT be None or empty!")
        if timestamp is None:
            raise ValueError("Timestamp MUST NOT be None!")

        point = Point(measurement)
        for tag in tags:
            point.tag(tag[0], tag[1])
        for value in values:
            point.field(value[0], value[1])
        point.time(timestamp)

        self.__sem.acquire()
        if len(self.__buffer) >= self.__max_buffer_len:
            self.__pop_first(1)
        self.__buffer.append(point)
        self.__sem.release()

    def append_many(self, raw_point_list: List[
            Tuple[str, Union[List[Tuple[str, str]], None],
                  Union[List[Tuple[str, Any]], None], Any]]):
        """"
        Function which adds multiple measurement points at the end of the
        private list buffer.
        :param raw_point_list: List which contains multiple measurement points.
        For more information see function self.append().
        """
        point_list = []
        for raw_point in raw_point_list:
            if raw_point[0] is None:
                raise ValueError("node name MUST NOT be None!")
            if raw_point[0] == "":
                raise ValueError("node name MUST NOT be empty!")
            if raw_point[1] is None:
                tags = []
            else:
                tags = raw_point[1]
            if raw_point[2] is None or raw_point[2] == []:
                raise ValueError("value MUST NOT be None or emtpy!")
            if raw_point[3] is None:
                raise ValueError("Timestamp MUST NOT be None!")

            point = Point(raw_point[0])
            for tag in tags:
                point.tag(tag[0], tag[1])
            for value in raw_point[2]:
                point.field(value[0], value[1])
            point.time(raw_point[3])

        # If more points are polled than max_buffer_length we need to trim
        if len(point_list) > self.__max_buffer_len:
            point_list = point_list[-self.__max_buffer_len:]

        self.__sem.acquire()
        if len(self.__buffer) + len(point_list) > self.__max_buffer_len:
            self.__pop_first(
                len(self.__buffer) + len(point_list) - self.__max_buffer_len)
        self.__buffer = self.__buffer + point_list
        self.__sem.release()

    def write_points(self):
        """
        Function which writes points into the InfluxDB. If the transmission was
        successful, the points will be deleted from buffer.
        """
        self.__sem.acquire()
        if len(self.__buffer) > 1000:
            buffer_part = self.__buffer[:1000]
            status = self.__influx_wrapper.insert_many(buffer_part)
            if not status:  # successful
                self.__pop_first(len(buffer_part))
        else:
            status = self.__influx_wrapper.insert_many(self.__buffer)
            if not status:  # successful
                self.__buffer = []
        self.__sem.release()

    def __pop_first(self, number_of_elements: int):
        """
        Function which deletes the first n elements from the buffer.
        :param number_of_elements: Amount of elements to be deleted
        """
        if number_of_elements < 1:
            raise ValueError("Number of Elements to pop must be at least 1")
        if number_of_elements >= len(self.__buffer):
            raise ValueError(
                "Number of Elements to pop exceeds length of buffer")
        self.__buffer[0:number_of_elements - 1] = []
