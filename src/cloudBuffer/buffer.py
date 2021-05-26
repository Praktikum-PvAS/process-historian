from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class Buffer:
    def __init__(self, connection_params: dict): # ?Buffer needs connection_params?
        self._buffer = []

    @property
    def buffer(self):
        return self._buffer

    def append(self, node_name, value, timestamp):
        # TODO what about tags?
        self._buffer.append(Point(node_name).tag("useful", "tag").field("value", value).time(timestamp))

    def pop_first(self):
        self._buffer.pop(0)
