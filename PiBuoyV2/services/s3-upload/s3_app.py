#!/usr/bin/python3

import subprocess
import time
import os
import platform
from pathlib import Path

import schedule


S3_BUCKET = 's3://aisonobuoy-pibuoy-v2/compressed/'
FLASH_DIR = '/flash'
TELEMETRY_DIR = os.path.join(FLASH_DIR, 'telemetry')
S3_DIR = os.path.join(FLASH_DIR, 's3')
TELEMETRY_TYPES = [
    ('system', True), ('sensors', True), ('power', True), ('ais', True), ('hydrophone', False)]


def run_cmd(args, env=None):
    if env is None:
        env = os.environ.copy()
    print(f'running {args}')
    ret = -1
    try:
        ret = subprocess.check_call(args)
        print('%s returned %d' % (' '.join(args), ret))
    except subprocess.CalledProcessError as err:
        print('%s returned %s' % (' '.join(args), err))
    return ret == 0


def get_nondot_files(filedir):
    return [str(path).replace(filedir, '')[1:] for path in Path(filedir).rglob('*')
            if not os.path.basename(path).startswith('.')]


def s3_copy(filedir, aws='/usr/local/bin/aws'):
    for path in Path(filedir).rglob('*'):
        if os.path.isfile(path):
            s3_args = [aws, 's3', 'cp', str(path), S3_BUCKET]
            if run_cmd(s3_args):
                os.remove(path)


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


def job(hostname):
    timestamp = int(time.time())
    if not os.path.exists(S3_DIR):
        os.mkdir(S3_DIR)

    for telemetry, xz in TELEMETRY_TYPES:
        filedir = os.path.join(TELEMETRY_DIR, telemetry)
        if not os.path.exists(filedir):
            os.mkdir(filedir)
        tarfile = f'{S3_DIR}/{telemetry}-{hostname}-{timestamp}.tar'
        if xz:
            tarfile = tarfile + '.xz'
        print(f'processing {filedir}, tar {tarfile}')
        tar_dir(filedir, tarfile, xz=xz)
    s3_copy(S3_DIR)
    return


def main():
    hostname = os.getenv("HOSTNAME", platform.node())
    schedule.every().day.at("13:00").do(job, hostname)
    while True:
        schedule.run_pending()
        time.sleep(60)


if __name__ == '__main__':
    main()
