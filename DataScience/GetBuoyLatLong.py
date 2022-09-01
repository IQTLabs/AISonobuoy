import os
import json
import boto3
import numpy as np
import pandas as pd

import S3Utilities as s3

def list_thousand_plus_objects(bucket, prefix=None, file_ext=None):
    s3_client = boto3.client('s3')
    
    paginator = s3_client.get_paginator('list_objects_v2')
    response_iterator = paginator.paginate(Bucket=bucket, Prefix=prefix)

    file_names = []

    for response in response_iterator:
        for object_data in response['Contents']:
            key = object_data['Key']
            if key.endswith(file_ext):
                file_names.append(key)

    return file_names
    
if __name__ == "__main__":
    bucket = "aisonobuoy-pibuoy-v2"
    prefix = "compressed"
    label = "v3-mk1-2"
    
    r = list_thousand_plus_objects(bucket, prefix=prefix, file_ext=".json")

    if r:
        print(r)
    else:
        print(f"No objects found, returned: {r}")
