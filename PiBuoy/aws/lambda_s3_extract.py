import boto3
import json
import os
import tarfile
import urllib.parse
import uuid

print('Loading function')

s3 = boto3.client('s3')

def extract_files(download_path, upload_path):
    with tarfile.open(f'{download_path}', 'r') as _tar:
        if 'sensors' in download_path:
            _tar.extractall(f'{upload_path}/sensors')
        elif 'system' in download_path:
            _tar.extractall(f'{upload_path}/system')
        elif 'pindrop' in download_path:
            _tar.extractall(f'{upload_path}/pindrop')


def lambda_handler(event, context):
    print("Received event: " + json.dumps(event, indent=2))

    # Get the object from the event and show its content type
    bucket = event['Records'][0]['s3']['bucket']['name']
    key = urllib.parse.unquote_plus(event['Records'][0]['s3']['object']['key'], encoding='utf-8')
    try:
        response = s3.get_object(Bucket=bucket, Key=key)
        print("File:" + key)
        if response['ContentType'] == 'application/x-tar':
            print("Found a new compressed file, uncompressing")
            tmpkey = key.replace('/', '')
            download_path = '/tmp/{}{}'.format(uuid.uuid4(), tmpkey)
            upload_path = '/tmp/uncompressed-{}'.format(tmpkey)
            s3.download_file(bucket, key, download_path)
            extract_files(download_path, upload_path)
            print(upload_path)
            unique_id = str(uuid.uuid4())
            for root, dirs, files in os.walk(upload_path):
                for file in files:
                    newkey = ''
                    if 'sensors' in root:
                        newkey = 'sensors/'+file
                    elif 'system' in root:
                        newkey = 'system/'+file
                    elif 'pindrop' in root:
                        name, ext = file.split('.')
                        newkey = 'pindrop/'+name+unique_id+ext
                    if newkey:
                        print(f'Adding uncommpressed file: {newkey}')
                        s3.upload_file(os.path.join(root, file), f'{bucket}-processed', newkey)
        return 200
    except Exception as e:
        print(e)
        print('Error getting object {} from bucket {}. Make sure they exist and your bucket is in the same region as this function.'.format(key, bucket))
        raise e
