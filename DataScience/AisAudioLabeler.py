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
    download_path, bucket, prefix=None, label=None, force=False, decompress=False
):
    """Download all objects, optionally identified by their prefix and
    label, in an AWS S3 bucket to a local path. Check the
    ETag. Optionally decompress and, if appropriate, move extracted
    files by type.

    Parameters
    ----------
    download_path : pathlib.Path()
        The local path to which to download objects
    bucket : str
        The AWS S3 bucket
    prefix : str
        The AWS S3 prefix designating the object in the bucket
    label : str
        The label string contained in the object key
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

        # Skip objects for which the key does not contain the label
        if label is not None and label not in key:
            continue

        # Download the object if the corresponding file does not
        # exist, or forced
        if prefix is not None:
            os.makedirs(download_path / prefix, exist_ok=True)
        else:
            os.makedirs(download_path, exist_ok=True)
        if not (download_path / key).exists() or force:
            etag = s3.download_object(download_path, bucket, s3_object)
            logger.info(f"File {key} downloaded")
            if s3_object["ETag"].replace('"', "") != etag:
                logger.error("ETag does not check")
        else:
            logger.info(f"File {key} exists")

        # Optionally decompress
        if decompress:
            # Skip JSON status files
            if (download_path / key).suffix == ".json":
                logger.info(f"Skipping file {key}")
                continue
            with tarfile.open(download_path / key) as f:
                f.extractall(download_path)
                names = f.getnames()
            logger.info(f"Decompressed file {key}")

            # Move files by type
            for name in names:
                s = re.search(r"-([a-zA-Z_]+)\.", name)
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
    if not inp_path.exists():
        logger.error(f"Path {inp_path} does not exist")
        return
    positions = []
    position_keys = set(["mmsi", "status", "timestamp", "speed", "lat", "lon"])
    types = {}
    type_keys = set(["mmsi", "shiptype"])
    n_lines = 0
    n_positions = 0
    n_mmsis = 0
    names = os.listdir(inp_path)
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
                    # Collect samples containing the mapping from mmsi
                    # to shiptype
                    n_mmsis += 1
                    if sample["mmsi"] not in types:
                        types[sample["mmsi"]] = sample["shiptype"]

    ais = pd.DataFrame(positions).sort_values(by=["timestamp"], ignore_index=True)
    ais["shiptype"] = ais["mmsi"].apply(lambda x: types[x] if x in types else None)
    logger.info(f"Read {n_lines} lines")
    logger.info(f"Found {n_positions} positions")
    logger.info(f"Found {n_mmsis} mmsis")
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

        # Identify start timestamp from audio file name
        s = re.search(r"-([0-9]+)-[a-zA-Z]+\.", name)
        if s is not None:
            start_timestamp = s.group(1)
        else:
            start_timestamp = s.group(1)
        entry["start_timestamp"] = int(start_timestamp)
        entries.append(entry)
    hmd = pd.DataFrame(entries).sort_values(by=["start_timestamp"], ignore_index=True)

    return hmd


def augment_ais_data(source, hydrophone, ais, hmd):
    """Augment AIS dataframe with distance from the hydrophone, speed,
    and ship counts when underway, or not underway.

    Parameters
    ----------
    source : dict
        The source configuration
    hydrophone : dict
        The hydrophone configuration
    ais : pd.DataFrame()
        AIS position samples with ship type
    hmd : pd.DataFrame()
        Hydrophone metadata

    Returns
    -------
    ais : pd.DataFrame()
        AIS position samples with ship type and counts
    hmd : pd.DataFrame()
        Hydrophone metadata (unchanged)
    shp : dict
        AIS start and stop timestamps corresponding to each status
        interval

    """
    # Append AIS data columns
    ais["h"] = 0
    ais["distance"] = 0
    ais["speed"] = 0
    ais["shipcount_uw"] = 0
    ais["mmsis_uw"] = [[] for _ in range(len(ais.index))]
    ais["shipcount_nuw"] = 0
    ais["mmsis_nuw"] = [[] for _ in range(len(ais.index))]

    # Initialize ship counts
    min_t = int(min(ais["timestamp"].min(), hmd["start_timestamp"].min()))
    max_t = int(
        max(ais["timestamp"].max(), (hmd["start_timestamp"] + hmd["duration"]).max())
    )
    timestamp = np.array(range(min_t, max_t + 1))
    shipcount_uw = pd.DataFrame(
        {"count": np.zeros(timestamp.shape), "mmsis": [[] for _ in timestamp]},
        index=timestamp,
    )
    shipcount_nuw = pd.DataFrame(
        {"count": np.zeros(timestamp.shape), "mmsis": [[] for _ in timestamp]},
        index=timestamp,
    )

    # Consider each unique ship
    shp = {}
    groupby = ais.groupby(["mmsi"])
    n_group = 0
    for group in groupby:
        n_group += 1
        logger.info(f"Processing group {group[0]}")

        # Assign AIS dataframe
        ais_g = group[1].copy().reset_index()
        mmsi = ais_g["mmsi"].unique()
        if mmsi.size != 1:
            raise Exception("More than one MMSI found in group")
        else:
            mmsi = mmsi[0]
        if ais_g.shape[0] < 3:
            logger.info(f"Group {group[0]} has fewer than three reports: skipping")
            continue

        # Initialize SHP dictionary for tracking ship counts and
        # status intervals for each ship
        shp[mmsi] = {}

        # Compute source metrics and assign
        vld_t = ais_g["timestamp"].to_numpy()  # [s]
        vld_lambda = np.deg2rad(ais_g["lon"].to_numpy())  # [rad]
        vld_varphi = np.deg2rad(ais_g["lat"].to_numpy())  # [rad]
        vld_h = ais_g["h"].to_numpy()  # [m]
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
        ais.loc[ais["mmsi"] == mmsi, "distance"] = distance
        ais.loc[ais["mmsi"] == mmsi, "speed"] = speed

        # Consider each unique status
        for status in ais_g["status"].unique():
            logger.info(f"Processing status {status} for group {group[0]}")
            # See: https://www.navcen.uscg.gov/?pageName=AISMessagesA
            if status in ["UnderWayUsingEngine"]:
                timestamp_diff = 10  # [s]
            elif status in ["AtAnchor", "Moored", "NotUnderCommand"]:
                timestamp_diff = 180  # [s]
            else:
                timestamp_diff = 180  # [s]

            # Assign AIS dataframe and select columns
            ais_s = ais_g[ais_g["status"] == status]
            timestamp = ais_s["timestamp"].to_numpy()

            # Consider each interval during which the current ship has
            # the current status
            timestamp_sets = np.split(
                timestamp, np.where(np.diff(timestamp) > timestamp_diff)[0] + 1
            )
            shp[mmsi][status] = []
            for timestamp_set in timestamp_sets:
                start_timestamp = int(timestamp_set.min())
                stop_timestamp = int(timestamp_set.max())

                # Collect status intervals for each ship
                shp[mmsi][status].append((start_timestamp, stop_timestamp))

                # Update ship counts
                if status in ["UnderWayUsingEngine"]:
                    shipcount_uw.loc[start_timestamp:stop_timestamp, "count"] += 1
                    shipcount_uw.loc[start_timestamp:stop_timestamp, "mmsis"].apply(
                        lambda x: x.append(mmsi)
                    )
                elif status in ["AtAnchor", "Moored", "NotUnderCommand"]:
                    shipcount_nuw.loc[start_timestamp:stop_timestamp, "count"] += 1
                    shipcount_nuw.loc[start_timestamp:stop_timestamp, "mmsis"].apply(
                        lambda x: x.append(mmsi)
                    )

    # Assign ship counts and mmsis when underway, and not underway
    logger.info("Assigning ship counts underway")
    ais["shipcount_uw"] = ais["timestamp"].apply(lambda x: shipcount_uw.loc[x, "count"])
    logger.info("Assigning ship mmsis underway")
    ais["mmsis_uw"] = ais["timestamp"].apply(lambda x: shipcount_uw.loc[x, "mmsis"])
    logger.info("Assigning ship counts not underway")
    ais["shipcount_nuw"] = ais["timestamp"].apply(
        lambda x: shipcount_nuw.loc[x, "count"]
    )
    logger.info("Assigning ship mmsis not underway")
    ais["mmsis_nuw"] = ais["timestamp"].apply(lambda x: shipcount_nuw.loc[x, "mmsis"])

    return ais, hmd, shp


def get_ais_dataframe(data_home, source, force=False, ais=None):
    """Read AIS dataframe parquet, if it exists, or load AIS files as a
    dataframe and write parquet. Optionally force write an AIS
    dataframe parquet.

    Parameters
    ----------
    data_home : pathlib.Path()
        Path to directory containing data files
    source : dict
        The source configuration
    force : boolean
        Flag to force creation of the parquet, or not

    Returns
    -------
    ais : pd.DataFrame()
        AIS position samples with ship type

    """
    ais_parquet = data_home / source["name"] / source["label"] / "ais.parquet"
    if not ais_parquet.exists() or force:
        if ais is None:
            logger.info("Loading all AIS files")
            ais = load_ais_files(data_home / source["name"] / source["label"] / "ais")
        logger.info("Writing AIS parquet")
        ais.to_parquet(ais_parquet)
    else:
        logger.info("Reading AIS parquet")
        ais = pd.read_parquet(ais_parquet)
    return ais


def get_hmd_dataframe(data_home, hydrophone, force=False, hmd=None):
    """Read hydrophone metadata dataframe parquet, if it exists, or get
    hydrophone metadata as a dataframe and write parquet.

    Parameters
    ----------
    data_path : pathlib.Path()
        Path to directory containing data files
    hydrophone : dict
        The hydrophone configuration
    force : boolean
        Flag to force creation of the parquet, or not

    Returns
    -------
    hmd : pd.DataFrame()
        Hydrophone metadata

    """
    hmd_parquet = data_home / hydrophone["name"] / hydrophone["label"] / "hmd.parquet"
    if not hmd_parquet.exists() or force:
        if hmd is None:
            logger.info("Getting hydrophone metadata")
            hmd = get_hydrophone_metadata(
                data_home / hydrophone["name"] / hydrophone["label"] / "hydrophone"
            )
        logger.info("Writing hydrophone metadata parquet")
        hmd.to_parquet(hmd_parquet)
    else:
        logger.info("Reading HMD parquet")
        hmd = pd.read_parquet(hmd_parquet)
    return hmd


def get_shp_dictionary(data_home, source, force=False, shp=None):
    """Read SHP dictionary JSON, if it exists, or write SHP
    dictionary JSON, if SHP dictionary is not None.

    Parameters
    ----------
    data_home : pathlib.Path()
        Path to directory containing data files
    source : dict
        The source configuration
    force : boolean
        Flag to force creation of the JSON, or not
    shp : dict
        AIS start and stop timestamps corresponding to each status
        interval

    Returns
    -------
    shp : dict
        AIS start and stop timestamps corresponding to each status
        interval

    """
    shp_json = data_home / source["name"] / source["label"] / "shp.json"
    if shp_json.exists() and not force:
        logger.info("Reading SHP JSON")
        with open(shp_json, "r") as f:
            shp = json.load(f)
    else:
        if shp is None:
            raise Exception("Must provide SHP dataframe")
        logger.info("Writing SHP JSON")
        with open(shp_json, "w") as f:
            json.dump(shp, f)
    return shp


def plot_intervals(shp, hmd):
    """Plot ship status and hydrophone recording intervals.

    Parameters
    ----------
    shp : dict
        AIS start and stop timestamps corresponding to each status
        interval
    hmd : pd.DataFrame()
        Hydrophone metadata (unchanged)

    Returns
    -------
    None

    """
    fig, axs = plt.subplots()

    # Consider each ship
    n_ship = 0
    for mmsi, statuses in shp.items():
        n_ship += 1

        # Consider each status for the current ship
        for status, intervals in statuses.items():
            if status in ["UnderWayUsingEngine"]:
                color = "r"
            elif status in ["AtAnchor", "Moored", "NotUnderCommand"]:
                color = "b"
            else:
                color = "g"

            # Plot each interval for the current ship and status
            for interval in intervals:
                axs.plot(interval, [n_ship, n_ship], color)

    # Consider each hydrophone metadta entry
    xlim = axs.get_xlim()
    for iA in range(hmd.shape[0]):

        # Plot hydrophone recording intervals
        axs.plot(
            hmd["start_timestamp"][iA] + np.array([0, hmd["duration"][iA]]),
            n_ship + np.array([1, 1]),
            "k",
        )
    axs.set_xlim(xlim)

    # Label axes and show plot
    axs.set_xlabel("Timestamp [s]")
    axs.set_ylabel("Group")
    plt.show()


def plot_histogram(ais, max_n_ships):
    """Plot histogram of distance for times at which at most a
    specified maximum number of ships are reporting their status as
    underway.

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type and counts
    max_n_ships : int
        Maximum number of ships underway simultaneously

    Returns
    -------
    None

    """
    fig, axs = plt.subplots()
    axs.hist(
        ais.loc[ais["shipcount_uw"] <= max_n_ships, ["distance"]].to_numpy(), bins=100
    )
    axs.set_title("Distance")
    axs.set_xlabel("distance [m]")
    axs.set_ylabel("counts")
    plt.show()


def export_audio_clips(
    ais, hmd, shp, data_home, hydrophone, clip_home, max_n_ships, max_distance
):
    """Export audio clips from AIS intervals during which the
    specified maximum number of ships at the specified maximum
    distance are reporting their status as underway. Label the audio
    clip using the attributes of the ship closest to the hydrophone.

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type and counts
    hmd : pd.DataFrame()
        Hydrophone metadata (unchanged)
    shp : dict
        AIS start and stop timestamps corresponding to each status
        interval
    data_home : pathlib.Path()
        Path to directory containing data files
    hydrophone : dict
        The hydrophone configuration
    clip_home : pathlib.Path()
        Home directory for clip files
    max_n_ships : int
        Maximum number of ships underway simultaneously
    max_distance : float
        Maximum distance of ships underway simultaneously

    Returns
    -------
    n_audio_clips : int
        The number of exported audio clips

    """
    # Identify rows with no more than the specified number of ship at
    # the specified maximum distance are reporting their status as
    # underway
    status = "UnderWayUsingEngine"
    ais_columns = [
        "timestamp",
        "mmsi",
        "shiptype",
        "status",
        "distance",
        "mmsis_uw",
        "shipcount_uw",
    ]
    ais_g = ais.loc[
        (ais["status"] == status)
        & (ais["shipcount_uw"] <= max_n_ships)
        & (ais["distance"] <= max_distance),
        ais_columns,
    ]
    logger.info(f"Found {ais_g.shape[0]} ship groups")

    # Process each ship group
    n_clips = 0
    mmsis = []
    for index, row_g in ais_g.iterrows():
        mmsis_g = row_g["mmsis_uw"]

        # Consider each ship
        distance_m = float("+Infinity")
        interval_m = ()
        mmsi_m = ""
        shiptype_m = ""
        shipcount_m = ""
        timestamp = row_g["timestamp"]
        for mmsi in mmsis_g:

            # Skip ships previously selected
            if mmsi in mmsis:
                continue

            # Identify the interval corresponding to the current ship
            # and status
            found_interval = False
            for interval in shp[mmsi][status]:
                if interval[0] <= timestamp and timestamp <= interval[1]:
                    found_interval = True
                    break
            if not found_interval:
                raise Exception(f"Did not find interval for ship {mmsi}")

            # Identify the earliest AIS dataframe row for the current
            # ship within the interval and maximum distance
            rows_c = ais.loc[
                (ais["mmsi"] == mmsi)
                & (interval[0] <= ais["timestamp"])
                & (ais["timestamp"] <= interval[1])
                & (ais["distance"] <= max_distance),
                ais_columns,
            ]
            if rows_c.size == 0:
                continue
            else:
                row_c = rows_c.iloc[0]

            # Select the ship that is closest to the hydrophone
            if row_c["distance"] < distance_m:
                distance_m = row_c["distance"]
                mmsi_m = row_c["mmsi"]
                shiptype_m = row_c["shiptype"]
                shipcount_m = int(row_c["shipcount_uw"])
                interval_m = interval

        # Skip group if no ship selected
        if mmsi_m == "":
            continue

        # Collect selected ships
        mmsis.append(mmsi_m)
        logger.info(
            f"Selected ship {mmsi_m} at {distance_m:.1f} [m] among {shipcount_m} ships"
        )

        # Select the largest audio interval no larger than 540 seconds
        start_timestamp_0 = interval_m[0]
        start_timestamp_1 = min(interval_m[0] + 540, interval_m[1])

        # Identify the audio files corresponding to the audio
        # interval, and get the audio
        hmd_columns = ["name", "start_timestamp"]
        row_0 = hmd.loc[hmd["start_timestamp"] < start_timestamp_0, hmd_columns].iloc[
            -1
        ]
        row_1 = hmd.loc[hmd["start_timestamp"] < start_timestamp_1, hmd_columns].iloc[
            -1
        ]
        inp_path = data_home / hydrophone["name"] / hydrophone["label"] / "hydrophone"
        if row_0["start_timestamp"] == row_1["start_timestamp"]:
            # Get one audio file
            audio = lu.get_audio_file(inp_path / row_0["name"])

        else:
            # Get two audio files and concatenate
            audio_0 = lu.get_audio_file(inp_path / row_0["name"])
            audio_1 = lu.get_audio_file(inp_path / row_1["name"])
            audio = audio_0 + audio_1

        # Export the audio clip labeled using attributes of the
        # selected ship
        name = Path(row_0["name"]).stem
        start_t = (start_timestamp_0 - row_0["start_timestamp"]) * 1000  # [ms]
        stop_t = start_t + 540 * 1000  # [ms]
        wav_filename = f"{name}-{start_t}-{stop_t}-{mmsi_m}-{shiptype_m}-{status}-{distance_m:.1f}.wav"
        lu.export_audio_clip(audio, start_t, stop_t, clip_home / wav_filename)
        logger.info(f"Exported audio file {wav_filename}")
        n_clips += 1


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
        "--force-ais-parquet",
        action="store_true",
        help="force AIS parquet creation",
    )
    parser.add_argument(
        "--force-hmd-parquet",
        action="store_true",
        help="force hydrophone metadata parquet creation",
    )
    parser.add_argument(
        "--force-shp-json",
        action="store_true",
        help="force SHP JSON creation",
    )
    parser.add_argument(
        "-s",
        "--sampling-filepath",
        default=str(Path(__file__).parent / "data" / "sampling-ais.json"),
        help="the path of the sampling JSON file to process",
    )
    parser.add_argument(
        "--plot-intervals",
        action="store_true",
        help="do plot ship status and hydrophone recording intervals",
    )
    parser.add_argument(
        "--plot-histogram",
        action="store_true",
        help="do plot ship distance from hydrophone histogram",
    )
    parser.add_argument(
        "--export-clips",
        action="store_true",
        help="do export audio clips",
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

    # For now, assume strict source and hydrophone pairs
    if len(collection["sources"]) != len(collection["hydrophones"]):
        raise Exception("Strict source and hydrophone pairs expected")
    sources = collection["sources"]
    hydrophones = collection["hydrophones"]

    # Load file describing sampling cases
    sampling = lu.load_json_file(args.sampling_filepath)

    # For now, assume a single sampling case
    if len(sampling) > 1:
        raise Exception("Only one sampling case expected")
    case = sampling[0]

    # Handle each source and hydrophone pair
    for source, hydrophone in zip(sources, hydrophones):

        # Download all source files
        if (
            source["name"] != hydrophone["name"]
            or source["prefix"] != hydrophone["prefix"]
            or source["label"] != hydrophone["label"]
        ):
            raise Exception(
                "Source and hydrophone expected using the same name, prefix, and label"
            )
        download_buoy_objects(
            data_home / source["name"] / source["label"],
            source["name"],
            source["prefix"],
            source["label"],
            force=args.force_download,
            decompress=args.decompress,
        )

        # Get AIS data, hydrophone metadata, and augment AIS data with
        # distance, speed, and ship counts, if needed. Get corresponding
        # SHP data.
        ais = get_ais_dataframe(data_home, source, force=args.force_ais_parquet)
        hmd = get_hmd_dataframe(data_home, hydrophone, force=args.force_hmd_parquet)
        if "shipcount_uw" not in ais.columns or args.force_shp_json:
            ais, hmd, shp = augment_ais_data(source, hydrophone, ais, hmd)
            ais = get_ais_dataframe(data_home, source, force=True, ais=ais)
            shp = get_shp_dictionary(data_home, source, force=True, shp=shp)

        else:
            shp = get_shp_dictionary(data_home, source)

        # Plot ship status and hydrophone recording intervals
        if args.plot_intervals:
            plot_intervals(shp, hmd)

        # Plot histogram of distance for times at which at most a
        # specified maximum number of ships are reporting their status as
        # underway.
        if args.plot_histogram:
            plot_histogram(ais, case["max_n_ships"])

        # Export audio clips from AIS intervals during which two ships are
        # underway. Label the audio clip using the attributes of the ship
        # closest to the hydrophone.
        if args.export_clips:
            clip_home = Path(args.clip_home) / case["output_dir"]
            if not clip_home.exists():
                clip_home.mkdir(parents=True)
            export_audio_clips(
                ais,
                hmd,
                shp,
                data_home,
                hydrophone,
                clip_home,
                case["max_n_ships"],
                case["max_distance"],
            )

    return ais, hmd, shp


if __name__ == "__main__":
    ais, hmd, shp = main()
