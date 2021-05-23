# InfluxDB2.0 is used
# Only Writing is required
# For neccessary preparing see README - https://www.influxdata.com/blog/getting-started-with-python-and-influxdb-v2-0/
from influxdb_client import InfluxDBClient
from influxdb_client.client.write_api import SYNCHRONOUS
from influxdb import SeriesHelper

## connection to Database
# URL+Port
sURL="http://localhost:8086"
# token for authorization
sToken=""
# timeout-deafault=10000ms
sTimeout="5000"
# destination for writes and queries (db name)
sOrganization=""
sInfluxDBClient = InfluxDBClient(url=sURL, token=sToken, timeout=sTimeout, org=sOrganization)

if nNumberOfTagsToWrite > 1000 :
    #https://github.com/influxdata/influxdb-python/blob/master/examples/tutorial_serieshelper.py
    class MySeriesHelper(SeriesHelper):
    """Instantiate SeriesHelper to write points to the backend."""
        class Meta:
        """Meta class stores time series helper configuration."""
        # The client should be an instance of InfluxDBClient.
        client = sInfluxDBClient
        # The series name must be a string. Add dependent fields/tags
        # in curly brackets.
        series_name = 'events.stats.{server_name}'
        # Defines all the fields in this time series.
        fields = ['some_stat', 'other_stat']
        # Defines all the tags for the series.
        tags = ['server_name']
        # Defines the number of data points to store prior to writing
        # on the wire.
        bulk_size = 5
        # autocommit must be set to True when using bulk_size
        autocommit = True
    for sTagsToWrite in sTableOfTagsToWrite:
    # multiple writes in database
    # TODO: Anpassen der Parameter
    MySeriesHelper(server_name=sOrganization, fields)
    break
else :
    sMeasurement=""
    sTagValue=""
    sFieldValue=""
    fFieldValue=
    sPointToWrite = Point(sMeasurement).tag(sLocation).field(sFieldValue, fFieldValue)
    #bucketname from docker
    write_api.write(bucket=bucket, record=sPointToWrite)