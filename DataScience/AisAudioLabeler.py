from argparse import ArgumentParser
import json
import logging
import os
from pathlib import Path
import re
import shutil
import tarfile

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

import S3Utilities as s3
import LabelerUtilities as lu

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
        AIS position samples with ship type

    """
    positions = []
    position_keys = set(["mmsi", "status", "timestamp", "speed", "lat", "lon"])
    types = {}
    type_keys = set(["mmsi", "shiptype"])
    names = os.listdir(inp_path)
    n_lines = 0
    n_positions = 0
    n_types = 0
    for name in names:
        with open(inp_path / name, "r") as f:
            for line in f:
                n_lines += 1
                sample = json.loads(line)
                if position_keys.issubset(set(sample.keys())):
                    # Collect samples containing position
                    n_positions += 1
                    positions.append(sample)
                elif type_keys.issubset(set(sample.keys())):
                    # Collect samples containing the mapping from mmsi to shiptype
                    n_types += 1
                    if sample["mmsi"] not in types:
                        types[sample["mmsi"]] = sample["shiptype"]

    ais = pd.DataFrame(positions).sort_values(by=["timestamp"], ignore_index=True)
    ais["shiptype"] = ais["mmsi"].apply(lambda x: types[x] if x in types else None)
    logger.info(f"Read {n_lines} lines")
    logger.info(f"Found {n_positions} positions")
    logger.info(f"Found {n_types} types")
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
        entry = lu.probe_audio_file(inp_path / name)
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
    hmd = pd.DataFrame(entries).sort_values(by=["start_timestamp"], ignore_index=True)
    return hmd


def main():
    """Provide a command-line interface for the AisAudioLabeler module."""
    parser = ArgumentParser(description="Use AIS data to slice an audio file")
    parser.add_argument(
        "-D",
        "--data-home",
        default=str(Path("~").expanduser() / "Data" / "AISonobuoy"),
        help="the directory containing all downloaded AIS files",
    )
    parser.add_argument(
        "-c",
        "--collection-filename",
        default="collection-ais.json",
        help="the path of the collection JSON file to load",
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
    parser.add_argument(
        "-s",
        "--sampling-filepath",
        default=str(Path(__file__).parent / "data" / "sampling-ais.json"),
        help="the path of the sampling JSON file to process",
    )
    parser.add_argument(
        "-P",
        "--do-plot-metrics",
        action="store_true",
        help="do plot track with computed metrics",
    )
    parser.add_argument(
        "-C",
        "--clip-home",
        default=str(Path("~").expanduser() / "Datasets" / "AISonobuoy"),
        help="the directory containing clip WAV files",
    )
    args = parser.parse_args()
    data_home = Path(args.data_home)

    # Load file describing the collection
    collection_path = Path(args.data_home) / args.collection_filename
    collection = lu.load_json_file(collection_path)

    # Load file describing sampling cases
    sampling = lu.load_json_file(args.sampling_filepath)

    # For now, assume a single source and hydrophone
    if len(collection["sources"]) > 1 or len(collection["hydrophones"]) > 1:
        raise Exception("Only one source and one hydrophone expected")
    source = collection["sources"][0]
    hydrophone = collection["hydrophones"][0]

    # Download all source files
    if source["name"] != hydrophone["name"] or source["prefix"] != hydrophone["prefix"]:
        raise Exception(
            "Source and hydrophone expected using the same prefix from the same bucket"
        )
    download_buoy_objects(
        data_home / source["name"],
        source["name"],
        source["prefix"],
        force=args.force_download,
        decompress=args.decompress,
    )

    # Load all AIS files
    ais_pickle = data_home / source["name"] / "ais.pickle"
    if not ais_pickle.exists() or args.force_ais_pickle:
        logger.info("Loading all AIS files")
        ais = load_ais_files(data_home / source["name"] / "ais")
        logger.info("Writing AIS pickle")
        ais.to_pickle(ais_pickle)
    else:
        logger.info("Reading AIS pickle")
        ais = pd.read_pickle(ais_pickle)

    # Get hydrophone metadata
    hmd_pickle = data_home / hydrophone["name"] / "hmd.pickle"
    if not hmd_pickle.exists() or args.force_hmd_pickle:
        logger.info("Getting hydrophone metadata")
        hmd = get_hydrophone_metadata(data_home / hydrophone["name"] / "hydrophone")
        logger.info("Writing hydrophone metadata pickle")
        hmd.to_pickle(hmd_pickle)
    else:
        logger.info("Reading hydrophone metadata pickle")
        hmd = pd.read_pickle(hmd_pickle)

    # Plot AIS time intervals for each vessel and status
    # See:
    # https://www.navcen.uscg.gov/?pageName=AISMessagesA
    # https://gpsd.gitlab.io/gpsd/AIVDM.html#_types_1_2_and_3_position_report_class_a
    # https://github.com/M0r13n/pyais/blob/96e01d9f2fac380a87d4948cac2b236c6a1a7c4f/pyais/decode.py
    figUW, axsUW = plt.subplots()
    figNUW, axsNUW = plt.subplots()
    groupby = ais.groupby(["mmsi"])
    n_group = 0
    for group in groupby:
        n_group += 1
        logger.info(f"Processing group {group[0]}")

        # Assign AIS dataframe and add height
        ais_g = group[1]
        ais_g["h"] = 0

        # Ensure unique identity
        mmsi = ais_g["mmsi"].unique()
        if mmsi.size != 1:
            raise Exception("More than one MMSI found in group")

        # Consider each unique status
        for status in ais_g["status"].unique():
            logger.info(f"Processing status {status} for group {group[0]}")

            # Assign AIS dataframe and select columns
            ais_s = ais_g[ais_g["status"] == status]
            vld_t = ais_s["timestamp"].to_numpy()  # [s]
            vld_lambda = np.deg2rad(ais_s["lon"].to_numpy())  # [rad]
            vld_varphi = np.deg2rad(ais_s["lat"].to_numpy())  # [rad]
            vld_h = ais_s["h"].to_numpy()  # [m]

            delta_t_max = 540
            vld_t_sets = np.split(vld_t, np.where(np.diff(vld_t) > delta_t_max)[0] + 1)
            for vld_t_set in vld_t_sets:
                if status in ["UnderWayUsingEngine"]:
                    axsUW.plot([vld_t_set[0], vld_t_set[-1]], [n_group, n_group], "k")

                elif status in ["AtAnchor", "Moored", "NotUnderCommand"]:
                    axsNUW.plot([vld_t_set[0], vld_t_set[-1]], [n_group, n_group], "k")

            # Compute and plot source metrics for the current hydrophone
            (
                distance,
                heading,
                heading_dot,
                speed,
                r_s_h,
                v_s_h,
            ) = lu.compute_source_metrics(
                source, vld_t, vld_lambda, vld_varphi, vld_h, hydrophone
            )
            if args.do_plot_metrics:
                lu.plot_source_metrics(
                    source, hydrophone, heading, heading_dot, distance, speed, r_s_h
                )

    # Plot hydrophone time intervals
    for iA in range(hmd.shape[0]):
        axsUW.plot(
            hmd["start_timestamp"][iA] + np.array([0, hmd["duration"][iA]]),
            n_group + np.array([1, 1]),
            "k",
        )
        axsNUW.plot(
            hmd["start_timestamp"][iA] + np.array([0, hmd["duration"][iA]]),
            n_group + np.array([1, 1]),
            "k",
        )

    # Label axes and show plot
    axsUW.set_title("UnderWayUsingEngine")
    axsUW.set_xlabel("Timestamp [s]")
    axsUW.set_ylabel("Group")
    axsNUW.set_title("AtAnchor, Moored, NotUnderCommand")
    axsNUW.set_xlabel("Timestamp [s]")
    axsNUW.set_ylabel("Group")
    plt.show()

    return collection, sampling, ais, hmd


if __name__ == "__main__":
    collection, sampling, ais, hmd = main()
