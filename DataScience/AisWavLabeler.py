from argparse import ArgumentParser
import hashlib
import logging
from pathlib import Path

import S3Utilities as s3


# Logging configuration
root = logging.getLogger()
if not root.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)

logger = logging.getLogger("AisWavLabeler")
logger.setLevel(logging.INFO)


def download_object(download_path, bucket, s3_object):
    """Download an object from an AWS S3 bucket to a local path.

    Parameters
    ----------
    download_path : pathlib.Path()
        The local path to which to download objects
    bucket : str
        The AWS S3 bucket
    s3_object : dict
        The AWS S3 object

    Returns
    -------
    etag : str
        The ETag of the AWS S3 object

    Note that AWS S3 objects contain an ETag which is either an MD5
    sum of the file, or an MD5 sum of the concatenated MD5 sums of
    chunks of the file followed by a hypen and the number of chunks.

    See:
    https://zihao.me/post/calculating-etag-for-aws-s3-objects/
    https://botocore.amazonaws.com/v1/documentation/api/latest/reference/response.html
    """
    if "-" in s3_object["ETag"]:
        is_hyphenated = True
        md5s = []
        chunk_size = 8 * 1024 * 1024
    else:
        is_hyphenated = False
        md5 = hashlib.md5()
        chunk_size = 1024 * 1024
    key = s3_object["Key"]
    r = s3.get_object(bucket, key)
    with open(download_path / key, "wb") as f:
        for chunk in r["Body"].iter_chunks(chunk_size=chunk_size):
            f.write(chunk)
            if is_hyphenated:
                md5s.append(hashlib.md5(chunk).digest())
            else:
                md5.update(chunk)
    if is_hyphenated:
        md5 = hashlib.md5(b"".join(md5s))
        etag = f"{md5.hexdigest()}-{len(md5s)}"
    else:
        etag = md5.hexdigest()
    return etag


def download_objects(download_path, bucket, prefix=None):
    """Download all objects, optionally identified by their prefix, in
    an AWS S3 bucket to a local path. Check the ETag.

    Parameters
    ----------
    download_path : pathlib.Path()
        The local path to which to download objects
    bucket : str
        The AWS S3 bucket
    prefix : str
        The AWS S3 prefix designating the object in the bucket

    Returns
    -------
    None

    """
    if prefix is None:
        r = s3.list_objects(bucket)
    else:
        r = s3.list_objects(bucket, prefix=prefix)
    if r is not None:
        s3_objects = r["Contents"]
        for s3_object in s3_objects:
            key = s3_object["Key"]
            if (download_path / key).exists():
                logger.info(f"File {key} exists")
            else:
                etag = download_object(download_path, bucket, s3_object)
                logger.info(f"File {key} downloaded")
                if s3_object["ETag"].replace('"', "") != etag:
                    logger.error("ETag does not check")


"""Provide a command-line interface for the AisWavLabeler module.
"""
if __name__ == "__main__":
    parser = ArgumentParser(description="Use AIS data to slice a WAV file")
    parser.add_argument(
        "-b",
        "--bucket",
        default="aisonobuoy-pibuoy-v2",
        help="the AWS S3 bucket containing AIS files",
    )
    parser.add_argument(
        "-p",
        "--prefix",
        default="compressed",
        help="the prefix in the AWS S3 bucket designating AIS files",
    )
    parser.add_argument(
        "-D",
        "--data-home",
        default=str(Path("~").expanduser() / "Data" / "AISonobuoy" / "AIS"),
        help="the directory containing all downloaded AIS files",
    )
    args = parser.parse_args()

    # Download all AIS files
    download_objects(Path(args.data_home), args.bucket, prefix=args.prefix)
