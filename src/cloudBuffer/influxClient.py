from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS


class InfluxClient:  # renamed so not as imported class
    def __init__(self, connection_params: dict):
        # TODO connection parameters need structure to use
        self._url = connection_params.url  # TODO Change this later
        self._token = connection_params.token  # TODO Change this later
        self._bucket = connection_params.bucket  # TODO Change this later
        self.influxDBClient = InfluxDBClient(self._url, self._token)
        self.write_api = self.influxDBClient.write_api(write_options=SYNCHRONOUS)

    def insert(self, buffer: Buffer):
        self.write_api.write(bucket=self._bucket, record=buffer)
        # TODO check if written successfully
        # TODO pop written data of buffer
