# Process-Historian
A simple client that connects to different interfaces to pull, parse and archive data.

## Usage
### Edit the config
Before your first start of the Process Historian, you have to edit the file `config/program_config.yaml`. \
Every time you edit the config after the first start, you have to restart the ProcessHistorian.

| Parameter          | Type   | Required     | Description |
| ------------------ | ------ | ------------ | ----------- |
| heartbeat_interval | number | **Optional** | Interval in milliseconds for the check if the OPC UA connection is alive. Defaults to 1000. |
| include            | list   | **Required** | Defines which types of DataAssembly are polled from the TripleStore and configured for the OPC UA. Values can be `sensors`, `actuators` and `services`. |
| buffer             | map    | **Required** | Parameter for the CloudBuffer. |
| influxdb           | map    | **Required** | Parameter for the InfluxDB. |
| tripleStore        | map    | **Required** | Parameter for the TripleStore. |

#### Buffer parameters
| Parameter     | Type   | Required     | Description |
| ------------- | ------ | ------------ | ----------- |
| size          | number | **Required** | Maximum buffer size. After running full every new data point replaces the oldest. |
| push_interval | number | **Optional** | Interval in milliseconds when the current buffer is pushed to the InfluxDB. |

#### InfluxDB parameters
| Parameter    | Type   | Required     | Description |
| ------------ | ------ | ------------ | ----------- |
| host         | url    | **Required** | Host of the InfluxDB |
| token        | string | **Required** | Access token. Needs at least read and write access for the specified bucket. |
| bucket       | string | **Required** | Bucket where the data should be pushed to. |
| organization | string | **Required** | Organization in the InfluxDB |

#### TripleStore parameters
| Parameter | Type   | Required     | Description |
| --------- | ------ | ------------ | ----------- |
| host      | url    | **Required** | Host of the TripleStore. Required even if it's not doing anything right now. |
| username  | string | **Optional** | Username for the TripleStore. Currently not used in program |
| password  | string | **Optional** | Password for the TripleStore. Currently not used in program |

### Using Docker
All the following commands may require elevated privileges (e.g., being root-user or use `sudo`).
#### Build the image
Building the image using Dockerfile:
```bash
$ docker build -t process-historian .
```
It's also possible to use docker-compose:
```bash
$ docker-compose build
```

#### Run the image
A container can be started by using:
```bash
$ docker run --rm -v "$(pwd)"/config:/usr/app/config process-historian
```
Be sure to mount the config folder else the program won't work. \
If you want to start the container in detached mode, use:
```bash
$ docker run --rm -d -v "$(pwd)"/config:/usr/app/config process-historian
```

Docker-compose can be used here too:
```bash
$ docker-compose up
```
Or, if you want to start the container in detached mode use:
```bash
$ docker-compose up -d
```

### Without using docker
#### Requirements
- Python 3.8+
- pip

#### Installing dependencies
Dependencies can be installed in a [virtual environment](https://docs.python.org/3/tutorial/venv.html).
If you don't use a virtual environment, the installation may require elevated rights.
```bash
$ pip3 install -r requirements.txt
```
On Windows the command is called `pip` (without the `3`).

#### Running the application
If you installed the requirements in a virtual environment, you must activate it before starting the application.
```bash
$ python3 src/processHistorian.py
```
On Windows the command is called `python` (without the `3`).

## Running tests
Tests are written in the python unittest library