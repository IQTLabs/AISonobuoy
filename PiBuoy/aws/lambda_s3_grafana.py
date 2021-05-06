import asyncio
import base64
import boto3
import functools
import json
import math
import os
import s3fs
import time
import uuid

from calendar import timegm
from datetime import datetime


def convert_to_time_ms(timestamp):
    return 1000 * timegm(
            datetime.strptime(
                timestamp, '%Y-%m-%dT%H:%M:%S.%fZ').timetuple())
                
   
def get_matching_s3_keys(bucket, prefix='', suffix=''):
    """
    Generate the keys in an S3 bucket.

    :param bucket: Name of the S3 bucket.
    :param prefix: Only fetch keys that start with this prefix (optional).
    :param suffix: Only fetch keys that end with this suffix (optional).
    """
    s3 = boto3.client('s3')
    kwargs = {'Bucket': bucket}

    # If the prefix is a single string (not a tuple of strings), we can
    # do the filtering directly in the S3 API.
    if isinstance(prefix, str):
        kwargs['Prefix'] = prefix

    while True:

        # The S3 API response is a large blob of metadata.
        # 'Contents' contains information about the listed objects.
        resp = s3.list_objects_v2(**kwargs)
        for obj in resp['Contents']:
            key = obj['Key']
            if key.startswith(prefix) and key.endswith(suffix):
                yield key

        # The S3 API is paginated, returning up to 1000 keys at a time.
        # Pass the continuation token into the next response, until we
        # reach the final page (when this field is missing).
        try:
            kwargs['ContinuationToken'] = resp['NextContinuationToken']
        except KeyError:
            break
        
        
def get_files_in_range(start, end):
    files = []
    bucket = 'biggerboatwest-processed'
    for key in get_matching_s3_keys(bucket=bucket, prefix='sensors/', suffix='.json'):
        # add an hour buffer (in milliseconds) on the end since files are compressed hourly
        if int(key.split('-')[1]) >= start and int(key.split('-')[1]) <= end+3600000:
            files.append(f'{bucket}/{key}')
    return files
    

def process_file(file, requested_targets):
    s3 = s3fs.S3FileSystem(anon=False)
    print(f'started: {time.time()}')
    records = []
    with s3.open(file, 'r') as f:
        for line in f:
            record = json.loads(line)
            if record['target'] not in requested_targets:
                continue
            records.append(record)
    print(f'ended: {time.time()}')
    return records


async def get_s3_data(files, requested_targets):
    loop = asyncio.get_event_loop()
    answers = []
    requests = []
    print(files)
    for file in files:
        requests.append(loop.run_in_executor(None, functools.partial(process_file, file, requested_targets)))
    return await asyncio.gather(*requests)
    
    
def query(body):
    print(body)
    body = json.loads(body)
    start, end = body['range']['from'], body['range']['to']
    start = convert_to_time_ms(start)
    end = convert_to_time_ms(end)
    files = get_files_in_range(start, end)
    requested_targets = []
    for t in body['targets']:
        requested_targets.append(t['target'])
    
    targets = {}
    body = []
    counter = 0
    
    loop = asyncio.get_event_loop()
    answers = loop.run_until_complete(get_s3_data(files, requested_targets))
    loop.close()
    for answer in answers:
        for record in answer:
            if record['target'] in targets:
                body[targets[record['target']]]['datapoints'].extend(record['datapoints'])
            else:
                targets[record['target']] = counter
                body.append(record)
                counter += 1
    return body
                        
                        
def lambda_handler(event, context):
    if event['requestContext']['resourceId'] in ['GET /', 'OPTIONS /']:
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
            },
            'body': json.dumps('OK')
        }
    elif event['requestContext']['resourceId'] == 'POST /query':
        #b = base64.b64decode(event['body'])
        #body = query(b.decode("utf-8"))
        body = query(event['body'])
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
            },
            'body': json.dumps(body)
        }
    elif event['requestContext']['resourceId'] == 'POST /search':
        return {
            'statusCode': 200,
            'headers': {
                "Content-Type": "application/json",
            },
            'body': json.dumps(['roll',
                                'pitch',
                                'yaw',
                                'acceleration_x',
                                'acceleration_y',
                                'acceleration_z',
                                'gyroscope_x',
                                'gyroscope_y',
                                'gyroscope_z',
                                'magnetic_x',
                                'magnetic_y',
                                'magnetic_z',
                                'temperature',
                                'pressure',
                                'pressure_temperature',
                                'humidity',
                                'soc',
                                'uptime',
                                'cputempc',
                                'loadavg1m',
                                'loadavg5m',
                                'loadavg15m',
                                'mean1mRpiCurrent_window_diffs',
                                'mean1mSupplyVoltage_window_diffs',
                                'cputempc_window_diffs',
                                'error',
                                'rpiCurrent',
                                'supplyVoltage',
                                'mean1mSupplyVoltage',
                                'mean1mRpiCurrent',
                                'min1mSupplyVoltage',
                                'min1mRpiCurrent',
                                'max1mSupplyVoltage',
                                'max1mRpiCurrent',
                                'meanValid',
                                'powerState',
                                'powerStateOverride',
                                'version'])
        }
    return {
        'statusCode': 500,
        'body': json.dumps('Not a valid method!')
    }

