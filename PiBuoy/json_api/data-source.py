import json
import math
import os
import tarfile

from datetime import datetime
from calendar import timegm
from bottle import (Bottle, HTTPResponse, run, request, response,
                    json_dumps as dumps)


app = Bottle()
DATA_DIR = '/files'


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())


def extract_files(files):
    for f in files:
        with tarfile.open(f'{DATA_DIR}/{f}', 'r') as _tar:
            if f.startswith('sensors'):
                _tar.extractall(f'{DATA_DIR}/sensors')
            elif f.startswith('system'):
                _tar.extractall(f'{DATA_DIR}/system')
        os.remove(f'{DATA_DIR}/{f}')


def get_files_in_range(start, end):
    files = []
    _, dirnames, filenames = next(os.walk(DATA_DIR))
    extract_files(filenames)
    if 'sensors' in dirnames:
        _, _, filenames = next(os.walk(f'{DATA_DIR}/sensors'))
        for filename in filenames:
            # add an hour buffer (in milliseconds) on the end since files are compressed hourly
            if int(filename.split('-')[1]) >= start and int(filename.split('-')[1]) <= end+3600000:
                files.append(filename)
    print(files)
    return files


@app.hook('after_request')
def enable_cors():
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, OPTIONS'
    response.headers['Access-Control-Allow-Headers'] = \
        'Origin, Accept, Content-Type, X-Requested-With, X-CSRF-Token'


@app.route("/", method=['GET', 'OPTIONS'])
def index():
    return "OK"


@app.post('/search')
def search():
    # TODO read from file, don't hardcode
    return HTTPResponse(body=dumps(['roll', 'pitch', 'yaw', 'acceleration_x', 'acceleration_y', 'acceleration_z', 'gyroscope_x', 'gyroscope_y', 'gyroscope_z', 'magnetic_x', 'magnetic_y', 'magnetic_z', 'temperature', 'pressure', 'pressure_temperature', 'humidity', 'soc', 'uptime', 'cputempc', 'loadavg1m', 'loadavg5m', 'loadavg15m', 'mean1mRpiCurrent_window_diffs', 'mean1mSupplyVoltage_window_diffs', 'cputempc_window_diffs', 'error', 'rpiCurrent', 'supplyVoltage', 'mean1mSupplyVoltage', 'mean1mRpiCurrent', 'min1mSupplyVoltage', 'min1mRpiCurrent', 'max1mSupplyVoltage', 'max1mRpiCurrent', 'meanValid', 'powerState', 'powerStateOverride', 'version']),
                        headers={'Content-Type': 'application/json'})


@app.post('/query')
def query():
    start, end = request.json['range']['from'], request.json['range']['to']
    start = convert_to_time_ms(start)
    end = convert_to_time_ms(end)
    files = get_files_in_range(start, end)
    requested_targets = []
    for t in request.json['targets']:
        requested_targets.append(t['target'])
    targets = {}
    body = []
    counter = 0
    for sample in files:
        with open(f'{DATA_DIR}/sensors/{sample}') as f:
            for line in f:
                record = json.loads(line)
                if record['target'] not in requested_targets:
                    continue
                if record['target'] in targets:
                    body[targets[record['target']]]['datapoints'].extend(record['datapoints'])
                else:
                    targets[record['target']] = counter
                    body.append(record)
                    counter += 1

    return HTTPResponse(body=dumps(body),
                        headers={'Content-Type': 'application/json'})


if __name__ == '__main__':
    run(app=app, host='0.0.0.0', port=8081)
