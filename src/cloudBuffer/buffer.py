from influxdb_client import Point
from influxWrapper import InfluxWrapper


class Buffer:
    def __init__(self, connection_params: dict):
        self.__buffer = []
        self.influxClient = InfluxWrapper(connection_params)

    def append(self, node_name, value, timestamp):
        # TODO structure?
        # TODO check buffersize
        self.__buffer.append(
            Point(node_name).tag("useful", "tag").field("value", value).time(
                timestamp))

    def write_points(self):
        if not len(self.__buffer) == 1:
            status = self.influxClient.insert(self.__buffer[0])
            if not status:     # successful
                self.__buffer.remove(0)
        elif len(self.__buffer) > 1:
            status = self.influxClient.insert_many(self.__buffer)
            if not status:     # successful
                self.__buffer.clear()
