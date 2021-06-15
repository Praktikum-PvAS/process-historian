from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions


class InfluxWrapper:  # renamed so not as imported class
    def __init__(self, connection_params: dict):
        if connection_params['host'] is None:
            raise ValueError("variable value of url is none")
        if connection_params['host'] == "":
            raise ValueError("url is empty")
        self.__url = connection_params['host']

        if connection_params['username'] is None:
            raise ValueError("variable value of username is none")
        if connection_params['username'] == "":
            raise ValueError("username is empty")
        self.__username = connection_params['username']

        if connection_params['password'] is None:
            raise ValueError("variable value of password is none")
        if connection_params['password'] == "":
            raise ValueError("password is empty")
        self.__password = connection_params['password']

        if connection_params['organization'] is None:
            raise ValueError("variable value of org is none")
        if connection_params['organization'] == "":
            raise ValueError("org is empty")
        self.__org = connection_params['organization']

        if connection_params["bucket"] is None:
            raise ValueError("variable value of bucket is none")
        if connection_params["bucket"] == "":
            raise ValueError("bucket is empty")
        self.__bucket = connection_params["bucket"]
        # TODO create Token from username and password
        token = self.__username + " " + self.__password
        self.influxDBClient = InfluxDBClient(url=self.url, token=token,
                                             org=self.org)
        self.write_api = self.influxDBClient.write_api(
            write_options=SYNCHRONOUS)

    def insert(self, point: Point):
        try:
            with self.influxDBClient.write_api() as _write_client:
                _write_client(bucket=self.__bucket, record=point)
            return 0
        except:
            # urllib.error.URLError
            return 1

    def insert_many(self, points: list[Point]):
        try:
            with self.influxDBClient.write_api(write_options=WriteOptions(
                    batch_size=len(points))) as _write_client:
                _write_client.write(self.__bucket, self.__org, points)
            return 0
        except:
            return 1
