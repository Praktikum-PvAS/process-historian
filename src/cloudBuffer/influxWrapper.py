from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS, WriteOptions


class InfluxWrapper:  # renamed so not as imported class
    def __init__(self, connection_params: dict):
        self.url = connection_params['host']
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
        self.org = connection_params['organization']
        self.bucket = connection_params['bucket']
        # TODO create Token from username and password
        token = self.__username + " " + self.__password
        self.influxDBClient = InfluxDBClient(url=self.url, token=token,
                                             org=self.org)
        self.write_api = self.influxDBClient.write_api(
            write_options=SYNCHRONOUS)

    # property methods
    @property
    def url(self):
        return self._url

    @property
    def org(self):
        return self._org

    @property
    def bucket(self):
        return self._bucket

    # setter methods
    @url.setter
    def url(self, url):
        if url is None:
            raise ValueError("variable value of url is none")
        if url == "":
            raise ValueError("url is empty")
        self._url = url

    @org.setter
    def org(self, org):
        if org is None:
            raise ValueError("variable value of org is none")
        if org == "":
            raise ValueError("org is empty")
        self._org = org

    @bucket.setter
    def bucket(self, bucket):
        if bucket is None:
            raise ValueError("variable value of bucket is none")
        if bucket == "":
            raise ValueError("bucket is empty")
        self._bucket = bucket

    def insert(self, point):
        try:
            with self.influxDBClient.write_api() as _write_client:
                _write_client(bucket=self._bucket, record=point)
            return 0
        except:
            # urllib.error.URLError
            return 1

    def insert_many(self, points):
        try:
            with self.influxDBClient.write_api(write_options=WriteOptions(
                    batch_size=len(points))) as _write_client:
                _write_client.write(self.bucket, self.org, points)
            return 0
        except:
            return 1
