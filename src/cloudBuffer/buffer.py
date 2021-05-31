from influxdb_client import InfluxDBClient, Point


class Buffer:
    def __init__(self,
                 connection_params: dict):  # ?Buffer needs connection_params?
        self._buffer = []

    @property
    def buffer(self):
        return self._buffer

    def append(self, node_name, value, timestamp):
        # TODO what about tags?
        self._buffer.append(
            Point(node_name).tag("useful", "tag").field("value", value).time(
                timestamp))

    def delete_points(self, number_of_element):  # delete points from list
        self._buffer.remove(number_of_element)

    def clear_list(self):  # clearing all values from list
        self._buffer.clear()

    def get_number_of_points(self):  # number of points in buffer
        number_of_points = len(self._buffer)
        return number_of_points

    def pop_first(self, number_of_element):
        first_values = self._buffer.pop(number_of_element)
        return first_values
