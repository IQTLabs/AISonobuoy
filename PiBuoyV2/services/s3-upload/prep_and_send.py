#!/usr/bin/python3

from datetime import datetime
import subprocess
import time
import os
import platform
from pathlib import Path


START_SLEEP = 3600
S3_BUCKET = 's3://aisonobuoy-pibuoy-v2/compressed/'
FLASH_DIR = '/flash'
S3_DIR = os.path.join(FLASH_DIR, 's3')
TELEMETRY_TYPES = [
    ('system', True), ('power', True), ('ais', True), ('hydrophone', False)]


def run_cmd(args, env=None):
    if env is None:
        env = os.environ.copy()
    print(f'running {args}')
    ret = subprocess.check_call(args)
    if not ret:
        print('%s returned %d' % (' '.join(args), ret))


def get_nondot_files(filedir):
    return [str(path).replace(filedir, '')[1:] for path in Path(filedir).rglob('*')
            if not os.path.basename(path).startswith('.')]


def s3_copy(filedir):
    for path in Path(filedir).rglob('*'):
        if os.path.isfile(path):
            s3_args = ['/usr/local/bin/aws', 's3', 'cp', str(path), S3_BUCKET]
            run_cmd(s3_args)


def tar_dir(filedir, tarfile, xz=False):
    nondot_files = get_nondot_files(filedir)
    if nondot_files:
        tar_args = ['/usr/bin/tar', '--remove-files', '--sort=name', '-C', filedir]
        if xz:
            tar_args.append('-J')
        tar_args.extend(['-cf', tarfile])
        tar_args.extend(nondot_files)
        run_cmd(tar_args, env={'XZ_OPT': '-9'})
        return True
    print(f'no files found in {filedir}')
    return False


def main():
    time.sleep(START_SLEEP)
    hostname = platform.node()
    now = datetime.now()
    timestamp = now.strftime('%s%f')
    if not os.path.exists(S3_DIR):
        os.mkdir(S3_DIR)

    for telemetry, xz in TELEMETRY_TYPES:
        filedir = os.path.join(FLASH_DIR, telemetry)
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        tarfile = f'{S3_DIR}/{telemetry}-{hostname}-{timestamp}.tar'
        if xz:
            tarfile = tarfile + '.xz'
        print(f'processing {filedir}, tar {tarfile}')
        tar_dir(filedir, tarfile, xz=xz)
    s3_copy(S3_DIR)


if __name__ == '__main__':
    main()
