from typing import List

from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import WriteOptions, WriteType


class InfluxWrapper:  # renamed so not as imported class
    def __init__(self, connection_params: dict):
        if connection_params['host'] is None:
            raise ValueError("variable value of url is none")
        if connection_params['host'] == "":
            raise ValueError("url is empty")
        self.__url = connection_params['host']

        if connection_params['token'] is None:
            raise ValueError("variable value of token is none")
        if connection_params['token'] == "":
            raise ValueError("token is empty")
        self.__token = connection_params['token']

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

        self.__influxDBClient = InfluxDBClient(url=self.__url, token=self.__token,
                                               org=self.__org)

    def insert(self, point: Point):
        if point is None:
            raise ValueError("Point MUST NOT be None!")
        try:
            with self.__influxDBClient.write_api(
                    write_options=WriteOptions(max_retries=0, write_type=WriteType.synchronous)) as write_client:
                write_client(bucket=self.__bucket, record=point)
            return 0
        except:
            # urllib.error.URLError
            return 1

    def insert_many(self, points: List[Point]):
        if points is None:
            raise ValueError("Point list must not be None!")
        if points is []:
            raise ValueError("Point list must not be empty!")
        try:
            with self.__influxDBClient.write_api(write_options=WriteOptions(
                    batch_size=len(points), max_retries=0, write_type=WriteType.synchronous)) as write_client:
                write_client.write(self.__bucket, self.__org, points)
            return 0
        except:
            return 1
