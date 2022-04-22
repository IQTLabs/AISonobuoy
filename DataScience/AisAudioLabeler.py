from argparse import ArgumentParser
import json
import logging
import os
from pathlib import Path
import re
import shutil
import tarfile

import pandas as pd

import S3Utilities as s3
import Utilities as u

# Logging configuration
root_logger = logging.getLogger()
if not root_logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

logger = logging.getLogger("AisAudioLabeler")
logger.setLevel(logging.INFO)


def download_buoy_objects(
    download_path, bucket, prefix=None, force=False, decompress=False
):
    """Download all objects, optionally identified by their prefix, in
    an AWS S3 bucket to a local path. Check the ETag. Optionally
    decompress and, if appropriate, move extracted files by type.

    Parameters
    ----------
    download_path : pathlib.Path()
        The local path to which to download objects
    bucket : str
        The AWS S3 bucket
    prefix : str
        The AWS S3 prefix designating the object in the bucket
    force : boolean
        Force download
    decompress : boolean
        Decompress downloaded files

    Returns
    -------
    None

    """
    # List the objects in the bucket
    if prefix is None:
        r = s3.list_objects(bucket)
    else:
        r = s3.list_objects(bucket, prefix=prefix)
    if r is None:
        return

    # Consider each object
    s3_objects = r["Contents"]
    for s3_object in s3_objects:
        key = s3_object["Key"]

        # Download the object if the corresponding file does not
        # exist, or forced
        if not (download_path / key).exists() or force:
            etag = s3.download_object(download_path, bucket, s3_object)
            logger.info(f"File {key} downloaded")
            if s3_object["ETag"].replace('"', "") != etag:
                logger.error("ETag does not check")
        else:
            logger.info(f"File {key} exists")

        # Optionally decompress
        if decompress:
            with tarfile.open(download_path / key) as f:
                f.extractall(download_path)
                names = f.getnames()
            logger.info(f"Decompressed file {key}")

            # Move files by type
            for name in names:
                s = re.search(r"-([a-zA-Z]+)\.", name)
                if s is not None:
                    identifier = s.group(1)
                    copy_path = download_path / identifier
                    if not copy_path.exists():
                        os.mkdir(copy_path)
                    # TODO: Remove str() once using Python 3.9+
                    shutil.move(str(download_path / name), str(copy_path / name))


def load_ais_files(inp_path):
    """Load all AIS files residing on the input path containing
    required keys.

    Note that AIS files contain a single AIS sample using JSON on each
    line.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path to directory containing JSON files

    Returns
    -------
    ais : pd.DataFrame()
        AIS samples

    """
    samples = []
    req_keys = set(["speed", "lat", "lon"])
    names = os.listdir(inp_path)
    for name in names:
        with open(inp_path / name, "r") as f:
            for line in f:
                sample = json.loads(line)
                if not req_keys.issubset(set(sample.keys())):
                    continue
                samples.append(sample)
    ais = pd.DataFrame(samples)
    return ais


def get_hydrophone_metadata(inp_path):
    """Probe all audio files residing on the input path.
    
    Parameters
    ----------
    inp_path : pathlib.Path()
        Path to directory containing audio files

    Returns
    -------
    hmd : pd.DataFrame()
        Audio stream entries

    """
    entries = []
    req_keys = set(["sample_rate", "duration"])
    names = os.listdir(inp_path)
    for name in names:
        entry = u.probe_audio_file(inp_path / name)
        if not req_keys.issubset(set(entry.keys())):
            continue
        entry["sample_rate"] = int(entry["sample_rate"])
        entry["duration"] = float(entry["duration"])
        entry["name"] = name
        s = re.search(r"-([0-9]+)-[a-zA-Z]+\.", name)
        if s is not None:
            start_timestamp = s.group(1)
        else:
            start_timestamp = s.group(1)
        entry["start_timestamp"] = int(start_timestamp)
        entries.append(entry)
    hmd = pd.DataFrame(entries)
    return hmd


def main():
    """Provide a command-line interface for the AisAudioLabeler module."""
    parser = ArgumentParser(description="Use AIS data to slice a audio file")
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
        default=str(
            Path("~").expanduser() / "Data" / "AISonobuoy" / "aisonobuoy-pibuoy-v2"
        ),
        help="the directory containing all downloaded AIS files",
    )
    parser.add_argument(
        "-d",
        "--decompress",
        action="store_true",
        help="decompress downloaded files",
    )
    parser.add_argument(
        "--force-download",
        action="store_true",
        help="force file download",
    )
    parser.add_argument(
        "--force-ais-pickle",
        action="store_true",
        help="force AIS pickle creation",
    )
    parser.add_argument(
        "--force-hmd-pickle",
        action="store_true",
        help="force hydrophone metadata pickle creation",
    )
    args = parser.parse_args()
    data_home = Path(args.data_home)

    # Download all files
    download_buoy_objects(
        data_home,
        args.bucket,
        prefix=args.prefix,
        force=args.force_download,
        decompress=args.decompress,
    )

    # Load all AIS files
    logger.info("Loading all AIS files")
    ais_pickle = data_home / "ais.pickle"
    if not ais_pickle.exists() or args.force_ais_pickle:
        ais = load_ais_files(data_home / "ais")
        logger.info("Writing AIS pickle")
        ais.to_pickle(ais_pickle)
    else:
        logger.info("Reading AIS pickle")
        ais = pd.read_pickle(ais_pickle)

    # Get hydrophone metadata
    logger.info("Getting hydrophone metadata")
    hmd_pickle = data_home / "hmd.pickle"
    if not hmd_pickle.exists() or args.force_hmd_pickle:
        hmd = get_hydrophone_metadata(data_home / "hydrophone")
        logger.info("Writing hydrophone metadata pickle")
        hmd.to_pickle(hmd_pickle)
    else:
        logger.info("Reading hydrophone metadata pickle")
        hmd = pd.read_pickle(hmd_pickle)

    return ais, hmd

if __name__ == "__main__":
    ais, hmd = main()
