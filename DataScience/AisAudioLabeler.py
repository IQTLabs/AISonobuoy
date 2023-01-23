from argparse import ArgumentParser
from datetime import datetime
import json
import logging
import os
from pathlib import Path
import pickle
import re
import shutil
import tarfile

from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from scipy import signal

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

# Color-blind accessible color palette, https://gist.github.com/thriveth/8560036
CB_color_cycle = [
    "#ff7f00",
    "#377eb8",
    "#4daf4a",
    "#f781bf",
    "#a65628",
    "#984ea3",
    "#999999",
    "#e41a1c",
    "#dede00",
]

# Shiptype constants for plotting PSDs
SHIPTYPE_REMOVE_STRINGS = [
    "_NoAdditionalInformation",
    "_HazardousCategory_A",
    "_HazardousCategory_B",
    "_HazardousCategory_C",
    "_Reserved",
]
SHIPTYPE_SET_ONE = [
    "Cargo",
    "DredgingOrUnderwaterOps",
    "Tanker",
    "HSC",
    "Towing",
    "Tug",
]
SHIPTYPE_SET_TWO = [
    "ClassB",
    "LawEnforcement",
    "Passenger",
    "PleasureCraft",
    "Sailing",
    "SearchAndRescueVessel",
    "WIG",
]
PSD_PICKLE_FILE = "psd.pickle"


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


def load_ais_files(inp_path, speed_threshold=5.0):
    """Load all AIS files residing on the input path containing
    required keys.

    Note that AIS files contain a single AIS sample using JSON on each
    line.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path to directory containing JSON files
    speed_threshold : float
        Threshold below which the ship is not under way using engine
        [knots]

    Returns
    -------
    ais : pd.DataFrame()
        AIS position samples with ship type

    """
    if not inp_path.exists():
        logger.error(f"Path {inp_path} does not exist")
        return None
    positions = []
    position_keys = set(["mmsi", "status", "timestamp", "speed", "lat", "lon"])
    types = {}
    type_keys = set(["mmsi", "shiptype"])
    n_lines = 0
    n_positions = 0
    n_mmsis = 0
    names = os.listdir(inp_path)
    for name in names:
        if not name.endswith(".json"):
            continue
        with open(inp_path / name, "r", encoding="utf-8") as f:
            for line in f:
                n_lines += 1
                try:
                    sample = json.loads(
                        line
                    )  # TODO: to temporarily handle null bytes at EOF bug
                except json.decoder.JSONDecodeError:
                    print(f"JSON file w/ Error: {inp_path / name}")
                    continue

                # Exclude unneeded columns, currently only one, though more expected
                for key in [
                    "radio",
                ]:
                    _ = sample.pop(key, None)

                # Handle relevant AIS message types
                # See: https://www.navcen.uscg.gov/ais-messages
                if sample["type"] == 1 or sample["type"] == 2 or sample["type"] == 3:
                    # Class A Position Report
                    pass

                elif sample["type"] == 5:
                    # Class A Ship Static and Voyage Related Data
                    pass

                elif sample["type"] == 18:
                    # Class B Standard Equipment Position Report
                    if float(sample["speed"]) < speed_threshold:
                        sample["status"] = "NotUnderWayUsingEngine"
                    else:
                        sample["status"] = "UnderWayUsingEngine"

                elif sample["type"] == 24:
                    # Class B Static Data Report
                    sample["shiptype"] = "ClassB"

                # Collect either position or static data
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

        # Identify start timestamp from audio file name
        s = re.search(r"-([0-9]+)-[a-zA-Z]+\.", name)
        if s is None:
            continue
        start_timestamp = s.group(1)

        # All values present, so convert and append
        entry["sample_rate"] = int(entry["sample_rate"])
        entry["duration"] = float(entry["duration"])
        entry["name"] = name
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
    groupby = ais.groupby(["mmsi"], sort=False)
    for group in groupby:
        logger.info(f"Processing ship with mmsi: {group[0]} AIS data records")

        # Assign AIS dataframe
        ais_g = (
            group[1].copy().reset_index()
        )  # groups are tuples with (groupedbyval, group)
        if len(ais_g) < 3:
            logger.info(f"Group {group[0]} has fewer than three reports: skipping")
            continue

        # TODO: Is the MMSI available in the group?
        mmsi = ais_g["mmsi"].unique()
        mmsi = mmsi[0]

        # Initialize SHP dictionary for tracking ship counts and status intervals for each ship
        shp[mmsi] = {}  # TODO: Is a dictionary of dictionaries the best way to do this?

        # Compute source metrics and assign
        vld_t = ais_g["timestamp"].to_numpy()  # [s]
        vld_lambda = np.deg2rad(ais_g["lon"].to_numpy())  # [rad]
        vld_varphi = np.deg2rad(ais_g["lat"].to_numpy())  # [rad]
        vld_h = ais_g["h"].to_numpy()  # [m]
        (
            distance,
            _heading,
            _heading_dot,
            speed,
            _r_s_h,
            _v_s_h,
        ) = lu.compute_source_metrics(
            source, vld_t, vld_lambda, vld_varphi, vld_h, hydrophone
        )
        ais.loc[ais["mmsi"] == mmsi, "distance"] = distance
        ais.loc[ais["mmsi"] == mmsi, "speed"] = speed

        # Consider each unique status
        status_for_underway = ["UnderWayUsingEngine"]
        status_for_not_underway = [
            "NotUnderWayUsingEngine",
            "AtAnchor",
            "Moored",
            "NotUnderCommand",
        ]
        for status in ais_g["status"].unique():
            # TODO: Are we receiving every AIS message? We might not be ...
            logger.info(
                f"Processing status {status} records for ship with MMSI: {group[0]}"
            )
            # Assign timestamp differences by status
            # See: https://www.navcen.uscg.gov/?pageName=AISMessagesA
            if status in status_for_underway:
                timestamp_diff = 10  # [s]
            elif status in status_for_not_underway:  # Be explicit
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
                start_timestamp = int(timestamp_set[0])
                stop_timestamp = int(timestamp_set[-1])

                # Collect status intervals for each ship
                if start_timestamp != stop_timestamp:
                    shp[mmsi][status].append((start_timestamp, stop_timestamp))

                # Update ship counts
                if status in status_for_underway:
                    shipcount_uw.loc[start_timestamp:stop_timestamp, "count"] += 1
                    shipcount_uw.loc[start_timestamp:stop_timestamp, "mmsis"].apply(
                        lambda x: x.append(mmsi)
                    )
                elif status in status_for_not_underway:  # Be explicit
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
    data_home : pathlib.Path()
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
        with open(shp_json, "r", encoding="utf-8") as f:
            shp = json.load(f)
    else:
        if shp is None:
            raise Exception("Must provide SHP dataframe")
        logger.info("Writing SHP JSON")
        with open(shp_json, "w", encoding="utf-8") as f:
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
    fig, axs = plt.subplots(figsize=(10, 9), dpi=100)

    # Consider each ship
    n_ship = 0

    for _, statuses in shp.items():
        n_ship += 1

        # Consider each status for the current ship
        for status, intervals in statuses.items():
            if status in ["UnderWayUsingEngine"]:
                color = CB_color_cycle[0]  # orange
                label = "UnderWay Using Engine"
            elif status in ["AtAnchor", "Moored", "NotUnderCommand"]:
                color = CB_color_cycle[1]  # blue
                label = "Anchored/Moored/Not Under Command"
            else:
                color = CB_color_cycle[2]  # green
                label = "Other"

            # Plot each interval for the current ship and status
            for interval in intervals:
                axs.plot(interval, [n_ship, n_ship], color=color, label=label)

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
    plt.legend(
        *[*zip(*{l: h for h, l in zip(*axs.get_legend_handles_labels())}.items())][
            ::-1
        ],
        bbox_to_anchor=(1, 0),
        loc="lower right",
        bbox_transform=fig.transFigure,
        ncol=2,
    )
    plt.title("Recorded Ships with AIS Status")
    plt.show()


def plot_histogram(ais, max_n_ships, bins=100):
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
    _, axs = plt.subplots(figsize=(10, 9), dpi=100)
    underway_dists = ais.loc[
        (ais["shipcount_uw"] <= max_n_ships) & (ais["shipcount_uw"] > 0)
    ]["distance"]
    axs.hist(underway_dists.to_numpy(), bins=bins)
    axs.set_title("Count of Ships Reporting Underway by Distance")
    axs.set_xlabel("distance [m]")
    axs.set_ylabel("counts")
    if len(underway_dists) > bins:
        plt.yscale("log")
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
    for _, row_g in ais_g.iterrows():
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

            # TODO: Understand why some intervals are not found
            if not found_interval:
                logger.warning(f"Did not find interval for ship {mmsi}")
                continue

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


def upload_audio_clips(upload_path, bucket, prefix=None):
    """Upload all audio clips found on the upload path to the bucket
    with the prefix.

    Parameters
    ----------
    upload_path : pathlib.Path()
        The local path from which to upload audio clips
    bucket : str
        The AWS S3 bucket
    prefix : str
        The AWS S3 prefix designating the object in the bucket

    Returns
    -------
    None

    """
    for root, dirnames, filenames in os.walk(upload_path):
        for filename in filenames:
            filepath = Path(root) / filename
            if filepath.suffix == ".wav":
                if prefix is not None:
                    key = "/".join([prefix, filepath.name])
                else:
                    key = filepath.name
                with open(filepath, "rb") as f:
                    s3.put_object(f, bucket, key)


def get_psd_pickle(
    clip_home, S_dB_re_V_per_μPa, gain_dB, c_1=None, c_2=None, z_b=None, force=False
):
    """Read power spectral density pickle, if it exists, or compute
    source level and power spectral densities and pickle.

    Parameters
    ----------
    clip_home : pathlib.Path()
        Path to directory containing audio files
    S_dB_re_V_per_μPa : float
        Hydrophone sensitivity [dB re V/μPa]
    gain_dB : float
        Gain applied prior to analog to digital conversion [dB]
    c_1 : float
        Sound speed in the ocean [m/s]
    c_2 : float
        Sound speed in the bottom media [m/s]
    z_b : float
        Depth [m]
    force : boolean
        Flag to force creation of the pickle, or not

    Returns
    -------
    psd : dict
        Source levles and power spectral densities

    """
    psd_pickle = clip_home / PSD_PICKLE_FILE
    if not os.path.exists(psd_pickle) or force:
        logger.info("Computing SLs and PSDs")
        psd = use_audio_clips_to_compute_SL_and_PSD(
            clip_home,
            S_dB_re_V_per_μPa,
            gain_dB,
            c_1=None,
            c_2=None,
            z_b=None,
            force=force,
        )
        logger.info("Dumping power spectral densities pickle")
        with open(psd_pickle, "wb") as f:
            pickle.dump(psd, f, pickle.HIGHEST_PROTOCOL)
    else:
        logger.info("Loading power spectral densities pickle")
        with open(psd_pickle, "rb") as f:
            psd = pickle.load(f)
    return psd


def use_audio_clips_to_compute_SL_and_PSD(
    clip_home,
    S_dB_re_V_per_μPa,
    gain_dB,
    c_1=None,
    c_2=None,
    z_b=None,
    force=False,
):
    """Use exported audio clips to compute source level and power
    spectral density for each sample.

    Parameters
    ----------
    clip_home : pathlib.Path()
        Path to directory containing audio files
    S_dB_re_V_per_μPa : float
        Hydrophone sensitivity [dB re V/μPa]
    gain_dB : float
        Gain applied prior to analog to digital conversion [dB]
    c_1 : float
        Sound speed in the ocean [m/s]
    c_2 : float
        Sound speed in the bottom media [m/s]
    z_b : float
        Depth [m]
    force : boolean
        Flag to force creation of the power spectral densities pickle,
        or not

    Returns
    -------
    psd : dict
        Source levels and power spectral densities byship type, with
        intermediate values

    """
    psd = {}
    psd["clip_home"] = clip_home
    for audio_file in os.listdir(clip_home):
        if Path(audio_file).suffix != ".wav":
            continue

        # Parse name to obtain ship MMSI, type and range
        fields = audio_file.split("-")
        mmsi = fields[8]
        shiptype = fields[9]
        for r_s in SHIPTYPE_REMOVE_STRINGS:
            shiptype = fields[9].replace(r_s, "")
        if shiptype not in SHIPTYPE_SET_ONE and shiptype not in SHIPTYPE_SET_TWO:
            continue
        r = float(fields[11].replace(".wav", ""))  # [m]

        # Compute source level, propagation loss, mean square pressure,
        # sound pressure level, and power spectral densitry
        samples, sample_rate = lu.get_audio_samples(clip_home / audio_file)
        SL, PL, MSP, SPL, pressure = lu.compute_SL(
            samples, S_dB_re_V_per_μPa, gain_dB, r, c_1=c_1, c_2=c_2, z_b=z_b
        )
        f, PSD = signal.welch(pressure, fs=sample_rate, nperseg=sample_rate)
        # TODO: Move up to samples?
        if f.size == 0:
            continue

        # Assign and accumulate samples
        q = 100
        sample = {
            "audio_file": audio_file,
            "mmsi": mmsi,
            "r": r,
            "sample_rate": sample_rate / q,
            "pressure": pressure[::q],
            "SL": SL,
            "PL": PL,
            "MSP": MSP,
            "SPL": SPL,
            "f": f,
            "PSD": PSD,
        }
        if shiptype not in psd:
            psd[shiptype] = {}
            psd[shiptype]["f"] = f.copy()
            psd[shiptype]["SL"] = SL
            psd[shiptype]["PSD"] = PSD.copy()
            psd[shiptype]["samples"] = [sample]

        else:
            psd[shiptype]["SL"] += SL
            psd[shiptype]["PSD"] += PSD
            psd[shiptype]["samples"].append(sample)

    # Compute source level and power spectral density averages
    shiptypes = [t for t in psd.keys() if t != "clip_home"]
    for shiptype in shiptypes:
        n_samples = len(psd[shiptype]["samples"])
        psd[shiptype]["SL"] /= n_samples
        psd[shiptype]["PSD"] /= n_samples

    return psd


def write_SLs(psd, shiptypes, clip_home, tex_file):
    """Write source levels for the specified ship types as a LaTeX
    table.

    Parameters
    ----------
    psd : dict
        Source levels and power spectral densities
    shiptypes : list(str)
        Ship types to plot, currently exactly six
    clip_home : pathlib.Path()
        Path to directory containing audio files
    tex_file : str
        Name of LaTeX file

    Returns
    -------
    None

    """
    with open(clip_home / tex_file, "w") as f:

        # ̱Open environment
        line = "\\begin{tabular}{"
        for shiptype in shiptypes:
            line += "c"
        line += "}\n"
        f.write(line)

        # ̱Label table
        f.write("  \\hline\n")
        line = "  "
        for shiptype in shiptypes:
            if line != "  ":
                line += " & "
            line += f"\\textbf{{{shiptype[0:min(len(shiptype), 6)]}}}"
        line += " \\\\\n"
        f.write(line)
        f.write("  \\hline\n")
        f.write("  \\hline\n")

        # ̱Write at most ten samples for each ship type
        for iSmp in range(10):
            line = "  "
            for shiptype in shiptypes:
                if line != "  ":
                    line += " & "
                samples = psd[shiptype]["samples"]
                if iSmp < len(samples):
                    line += f"{samples[iSmp]['SL']:.1f}"
            line += " \\\\\n"
            f.write(line)
        f.write("  \\hline\n")

        # Write the average and number of samples for each ship type
        line = "  "
        for shiptype in shiptypes:
            if line != "  ":
                line += " & "
            line += f"{psd[shiptype]['SL']:.1f} ({len(psd[shiptype]['samples'])})"
        line += " \\\\\n"
        f.write(line)
        f.write("  \\hline\n")

        # Close environment
        f.write("\\end{tabular}\n")


def plot_psd(psd, plot_type, shiptypes, clip_home, plot_file):
    """Plot example pressure time series, or example or average power
    spectral densities for the specified ship types, and save the
    figure to the specified clip home.

    Parameters
    ----------
    psd : dict
        Pressure, source levels and power spectral densities
    plot_type : str
        Type of plot: "example_p_ts" (example pressure time series),
        "example_psd" (examples PSDs), or "average_psd" (averages
        PSDs)
    shiptypes : list(str)
        Ship types to plot, currently exactly six
    clip_home : pathlib.Path()
        Path to directory containing audio files
    plot_file : str
        Name of plot file

    Returns
    -------
    None

    """
    # Configure figure for subplots
    nRow = 2
    nCol = 3
    fig, axs = plt.subplots(nRow, nCol, figsize=(10, 5), layout="constrained")

    # Initialize common x and y axis limits
    if plot_type in ["example_psd", "average_psd"]:
        x0 = 2.0
        x1 = 2000.0
    y0 = float("inf")
    y1 = float("-inf")

    # Plot each ship type
    if plot_type in ["example_p_ts", "example_psd"]:
        mmsi = []
        SPL = []
    SL = []
    iTyp = -1
    for iRow in range(nRow):
        for iCol in range(nCol):
            iTyp += 1

            if plot_type in ["example_p_ts", "example_psd"]:
                item = psd[shiptypes[iTyp]]["samples"][0]
                mmsi.append(item["mmsi"])  # Accumulate for labeling
            else:
                item = psd[shiptypes[iTyp]]

            if plot_type == "example_p_ts":

                # Plot pressure over the full sample time
                SPL.append(item["SPL"])  # Accumulate for labeling
                pressure = item["pressure"]
                t = np.arange(pressure.size) / item["sample_rate"]
                axs[iRow, iCol].plot(t, pressure / 1.0e6)
                axs[iRow, iCol].set_title(
                    f"{shiptypes[iTyp][0:min(len(shiptypes[iTyp]), 12)]} ({mmsi[iTyp]})",
                    loc="left",
                )
                xlim = axs[iRow, iCol].get_xlim()
                x0 = xlim[0]
                x1 = xlim[1]

            else:

                # Plot spectrum over the x (frequency) limits
                SL.append(item["SL"])  # Accumulate for labeling
                f = item["f"]
                PSD = item["PSD"]
                idx = np.logical_and(x0 <= f, f <= x1)
                axs[iRow, iCol].loglog(f[idx], PSD[idx])
                if plot_type == "example_psd":
                    axs[iRow, iCol].set_title(
                        f"{shiptypes[iTyp][0:min(len(shiptypes[iTyp]), 12)]} ({mmsi[iTyp]})",
                        loc="left",
                    )
                else:
                    axs[iRow, iCol].set_title(f"{shiptypes[iTyp]}", loc="left")

            # Find common y limits
            ylim = axs[iRow, iCol].get_ylim()
            y0 = min(y0, ylim[0])
            y1 = max(y1, ylim[1])

    # Set common y limits, and annotate each subplot ...
    iTyp = -1
    for iRow in range(nRow):
        for iCol in range(nCol):
            iTyp += 1

            if plot_type == "example_p_ts":
                axs[iRow, iCol].set_ylim(y0, y1)
                xW = x1 - x0
                yW = y1 - y0
                aT = axs[iRow, iCol].text(
                    x0 + 0.05 * xW, y0 + 0.05 * yW, f"{SPL[iTyp]:.1f} dB re µPa²"
                )

            else:
                axs[iRow, iCol].set_ylim(y0, y1)
                aT = axs[iRow, iCol].text(x0, 2 * y0, f"{SL[iTyp]:.1f} dB re µPa²m²")

    # Label the axes of the figures of subplots
    if plot_type == "example_p_ts":
        xL = fig.supxlabel("Time [s]", fontweight="semibold")
        yL = fig.supylabel("Pressure [Pa]", fontweight="semibold")

    else:
        xL = fig.supxlabel("Frequency [Hz]", fontweight="semibold")
        yL = fig.supylabel("Pressure Spectral Density [µPa²/Hz]", fontweight="semibold")

    # Save the figure, then block for user input
    plot_path = clip_home / plot_file
    plt.savefig(plot_path, format=plot_path.suffix.replace(".", ""))
    plt.show()


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
    group = parser.add_mutually_exclusive_group()
    group.add_argument(
        "--force-download",
        action="store_true",
        help="force file download",
    )
    group.add_argument(
        "--skip-download",
        action="store_true",
        help="skip file download",
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
        help="force shp JSON creation",
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
        "--export-audio-clips",
        action="store_true",
        help="do export audio clips",
    )
    parser.add_argument(
        "-C",
        "--clip-home",
        default=str(Path("~").expanduser() / "Datasets" / "AISonobuoy"),
        help="the directory containing clip WAV files",
    )
    parser.add_argument(
        "--upload-audio-clips",
        action="store_true",
        help="do upload audio clips",
    )
    parser.add_argument(
        "--compute-sls-psds",
        action="store_true",
        help="use audio clips to compute source levels and power spectral densities",
    )
    parser.add_argument(
        "--force-psd-pickle",
        action="store_true",
        help="force psd pickle creation",
    )
    parser.add_argument(
        "--plot-psds",
        action="store_true",
        help="do plot power spectral densities",
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

        ais = None
        hmd = None
        shp = None
        if not args.skip_download:
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
                source["name"],  # bucket
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
            # closest to the hydrophone. Always delete exiting audio clips.
            if args.export_audio_clips:
                clip_home = Path(args.clip_home) / case["output_dir"]
                if not clip_home.exists():
                    clip_home.mkdir(parents=True)  # Make the directory
                else:
                    for p in clip_home.iterdir():  # Or remove all files
                        p.unlink()
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

        # Upload all audio clips found on the upload path to the
        # bucket with the prefix set a concatenation of "products" and
        # the current date
        if args.upload_audio_clips:
            clip_home = Path(args.clip_home) / case["output_dir"]
            if not clip_home.exists():
                raise Exception(f"Clip home {clip_home} does not exist")
            upload_audio_clips(
                clip_home,
                source["name"],  # bucket
                prefix="/".join(["products", datetime.now().strftime("%Y-%m-%d")]),
            )

        # Use exported audio clips to compute source level and power
        # spectral density for each clip, and plot
        psd = None
        if args.compute_sls_psds or args.plot_psds:
            clip_home = Path(args.clip_home) / case["output_dir"]
            if not clip_home.exists():
                raise Exception(f"Clip home {clip_home} does not exist")
            psd = get_psd_pickle(
                clip_home,
                hydrophone["S_dB_re_V_per_μPa"],
                hydrophone["gain_dB"],
                c_1=hydrophone["c_1"],
                c_2=hydrophone["c_2"],
                z_b=hydrophone["z_b"],
                force=args.force_psd_pickle,
            )
            if args.plot_psds:
                for iSet in range(2):
                    if iSet == 0:
                        base_name = "Ship-Type-Set-One"
                        shiptype_set = SHIPTYPE_SET_ONE
                    else:
                        base_name = "Ship-Type-Set-Two"
                        shiptype_set = SHIPTYPE_SET_TWO
                    write_SLs(
                        psd, SHIPTYPE_SET_ONE, clip_home, base_name + "-SL-Examples.tex"
                    )
                    plot_psd(
                        psd,
                        "example_p_ts",
                        shiptype_set,
                        clip_home,
                        base_name + "-Pressure-Examples.pdf",
                    )
                    plot_psd(
                        psd,
                        "example_psd",
                        shiptype_set,
                        clip_home,
                        base_name + "-Spectrum-Examples.pdf",
                    )
                    plot_psd(
                        psd,
                        "average_psd",
                        shiptype_set,
                        clip_home,
                        base_name + "-Spectrum-Averages.pdf",
                    )

    return ais, hmd, shp, psd


if __name__ == "__main__":
    ais, hmd, shp, psd = main()
