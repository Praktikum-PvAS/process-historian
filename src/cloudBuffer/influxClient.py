from influxdb_client import InfluxDBClient, Point
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb import SeriesHelper
from cloudBuffer.buffer import Buffer

# TODO send connection_params from buffer ti InfluxClient
class InfluxClient:  # renamed so not as imported class
    def __init__(self, connection_params: dict):
        self.url = connection_params['host']
        self.username = connection_params['username']
        self.password = connection_params['password']
        self.org = connection_params['organization']
        self.bucket = connection_params['bucket']

    # property methods
    @property
    def url(self):
        return self._url

    @property
    def username(self):
        return self._username

    @property
    def password(self):
        return self._password

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

    @username.setter
    def username(self, username):
        if username is None:
            raise ValueError("variable value of username is none")
        if username == "":
            raise ValueError("username is empty")
        self._username = username

    @password.setter
    def password(self, password):
        if password is None:
            raise ValueError("variable value of password is none")
        if password == "":
            raise ValueError("password is empty")
        self._password = password

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

        # TODO create Token from username and password
        token = self.username + "" + self.password
        self.influxDBClient = InfluxDBClient(url=self.url, token=token,
                                             org=self.org)
        self.write_api = self.influxDBClient.write_api(
            write_options=SYNCHRONOUS)

    def insert(self, buffer: Buffer):
        self.write_api.write(bucket=self._bucket,
                             record=buffer.pop_first(number_of_element=0))
        # TODO check if written successfully
        buffer.delete_points(number_of_element=0)  # delete single point

    def insert_many(self, buffer: Buffer):
        # TODO insert many points with MySeriesHelper
        # TODO https://github.com/influxdata/influxdb-python/blob/master/examples/tutorial_serieshelper.py

        buffer.clear_list()  # delete all points
