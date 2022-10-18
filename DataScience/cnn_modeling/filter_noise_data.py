# file handling
import os

# data manipulation
import numpy as np
from math import radians, cos, sin, asin, sqrt

# data formatting
import datetime
import pandas as pd

# audio data manipulation
from pydub import AudioSegment

# data directory filepath
ROOT = "/home/achadda/SonobuoyData/aisonobuoy-pibuoy-v2"

# filters
DEPLOYMENTS_OF_INTEREST = ["v2-mk2-3"]
STATUS_OF_INTEREST = "UnderWayUsingEngine"

# hydrophone file name components
HYDROPHONE_DATA_DIR = "hydrophone"
HYDROPHONE_RECORDING_FILETYPE = ".flac"
HYDROPHONE_PREFIX = "pibuoy-v2-mk2-3-"
HYDROPHONE_POSTFIX = "-hydrophone.flac"

# outputs
OUT_ROOT = "/home/achadda/tugboat_dataset/no_tugboat"
OUTPUT_DATA_FORMAT = ".wav"
OUTPUT_PREFIX = "noise_"
NOISE_ID = "0" * 9  # dummy mmsi
DEFAULT_INTERVAL_LENGTH_SECONDS = 600

# (lat, long)
CAPE_BUOY_LOCATION = (28.410868, -80.603866)
ANNAPOLIS_BUOY_LOCATION = (38.951455, -76.552497)

# find the nearest timestamp
def find_nearest(array, value):
    # minimum of the absolute value difference
    idx = (np.abs(array - value)).argmin()
    return idx


# Earth-as-a-sphere-based distance approximation using the Haversine formula
def distance_meters(lat_one, lon_one, lat_two, lon_two):
    earth_radius_km = 6371

    lat_one, lon_one, lat_two, lon_two = (
        radians(lat_one),
        radians(lon_one),
        radians(lat_two),
        radians(lon_two),
    )

    # Haversine formula
    return (
        2
        * asin(
            sqrt(
                sin((lat_two - lat_one) / 2) ** 2
                + cos(lat_one) * cos(lat_two) * sin((lon_two - lon_one) / 2) ** 2
            )
        )
        * earth_radius_km
    ) * 1000


# pull data files and ignore hidden files
data_dirs = [
    x
    for x in os.listdir(ROOT)
    if not x.startswith(".") and x in DEPLOYMENTS_OF_INTEREST
]

# pull parquet/json files w/ AIS info, hydrophone info, and ship info
files_of_interest = [
    y
    for y in os.listdir(os.path.join(ROOT, data_dirs[0]))
    if y.endswith(".parquet") or y.endswith(".json")
]

# create list of absolute file paths for each parquet
files_ls = []
for data_dir in data_dirs:
    for file in files_of_interest:
        files_ls.append(os.path.join(ROOT, data_dir, file))
files_ls.sort()  # ais, hmd, shp (alphabetical order)


# Cape Canaveral
v2mk2_ais_df = pd.read_parquet(files_ls[0])
v2mk2_hmd_df = pd.read_parquet(files_ls[1])
v2mk2_shp_df = pd.read_json(files_ls[2], convert_dates=False, convert_axes=False)

cape_ais = v2mk2_ais_df.copy()  # making human readable
v2mk2_ais_df = None  # free memory

# remove calibration artifacts w/ impossible lat/long
cape_latlon_cleaned = cape_ais.loc[
    (cape_ais.lon != 181.0) & (cape_ais.lat != 91.0)
].copy()

# add relative distance from buoy to each AIS entry
cape_latlon_cleaned.loc[:, "relative_distance_meters"] = cape_latlon_cleaned.apply(
    lambda row: distance_meters(
        CAPE_BUOY_LOCATION[0], CAPE_BUOY_LOCATION[1], row["lat"], row["lon"]
    ),
    axis=1,
)

# create output directories
os.makedirs(OUT_ROOT, exist_ok=True)

# isolate timestamp part of hydrophone recording filenames
hydrophone_files_ls = os.listdir(
    os.path.join(ROOT, DEPLOYMENTS_OF_INTEREST[0], HYDROPHONE_DATA_DIR)
)
hydrophone_timestamps_arr = np.array(
    sorted(
        [
            int(x.split("-")[4])
            for x in hydrophone_files_ls
            if x.endswith(HYDROPHONE_RECORDING_FILETYPE)
        ]
    )
)

# extract the data between 2AM and 3AM
files_ls = []
for val in [datetime.datetime.fromtimestamp(x) for x in hydrophone_timestamps_arr]:
    # 2AM in UTC time
    if val.hour == 21:
        files_ls.append(
            HYDROPHONE_PREFIX + str(int(val.timestamp())) + HYDROPHONE_POSTFIX
        )

# add a human readable date column
cape_latlon_cleaned.loc[
    cape_latlon_cleaned["timestamp"] > 0, "hrd"
] = cape_latlon_cleaned["timestamp"].apply(datetime.datetime.fromtimestamp)

# get all intervals where ships are underway to exclude them from ship json dataframe
shp_underway_intervals_to_exclude = [
    x
    for x in sum(
        v2mk2_shp_df.T["UnderWayUsingEngine"]
        .dropna()
        .apply(lambda x: np.nan if len(x) == 0 else x)
        .dropna()
        .to_list(),
        [],
    )
    if datetime.datetime.fromtimestamp(x[0]).hour == 21
    or datetime.datetime.fromtimestamp(x[1]).hour == 21
]

#
exclusion_dict = {}
for interval in shp_underway_intervals_to_exclude:
    # get the nearest hydrophone file
    closest_idx = find_nearest(hydrophone_timestamps_arr, interval[0]) - 1
    file_timestamp = hydrophone_timestamps_arr[closest_idx]

    # snippet to remove
    audio_to_exclude = [
        (int(interval[0]) - file_timestamp) * 1000,
        (int(interval[1]) - file_timestamp) * 1000,
    ]
    # add exclusion interval to
    if file_timestamp not in exclusion_dict.keys():
        exclusion_dict[file_timestamp] = [audio_to_exclude]
    else:
        exclusion_dict[file_timestamp].append(audio_to_exclude)

# for each hydrophone recording
for idx, _ in enumerate(hydrophone_timestamps_arr):
    timestamp = hydrophone_timestamps_arr[idx]
    # get sequnential files
    if idx != len(hydrophone_timestamps_arr) - 1:
        next_timestamp = hydrophone_timestamps_arr[idx + 1]
    else:
        next_timestamp = None

    # create filepath to save snippet
    file_path = os.path.join(
        ROOT,
        DEPLOYMENTS_OF_INTEREST[0],
        HYDROPHONE_DATA_DIR,
        HYDROPHONE_PREFIX + str(timestamp) + HYDROPHONE_POSTFIX,
    )

    # load audio recording from file
    try:
        audio = AudioSegment.from_file(
            file_path, format=HYDROPHONE_RECORDING_FILETYPE[1:]
        )
    # some file was corrupted
    except AttributeError:
        print("FAILED ON FILE:", file_path)
        continue

    if timestamp in exclusion_dict.keys():
        # parsing individuals by first/last
        # doing this for now b/c we are missing AIS readings
        exclusion_timestamps = sorted(exclusion_dict[timestamp])
        exclude_begin = exclusion_timestamps[0][0]
        exclude_end = exclusion_timestamps[-1][-1]

        # get the noise snippet before the exclusion timestamp
        audio_one = audio[:exclude_begin]
        audio_one.export(
            os.path.join(
                OUT_ROOT,
                OUTPUT_PREFIX
                + NOISE_ID
                + "_"
                + str(int(timestamp))
                + "_"
                + str(int(timestamp + exclude_begin / 1000))
                + OUTPUT_DATA_FORMAT,
            ),
            format=OUTPUT_DATA_FORMAT[1:],
        )

        # if the exclusion interval end is within the current file, save
        if exclude_end < len(audio) and exclude_end > 0:
            audio_two = audio[exclude_end:]
            audio_two.export(
                os.path.join(
                    OUT_ROOT,
                    OUTPUT_PREFIX
                    + NOISE_ID
                    + "_"
                    + str(int(timestamp + len(audio) / 1000 - exclude_end / 1000))
                    + "_"
                    + str(int(timestamp + len(audio) / 1000))
                    + OUTPUT_DATA_FORMAT,
                ),
                format=OUTPUT_DATA_FORMAT[1:],
            )
        # if it's before the interval, ignore
        elif exclude_end < 0:
            continue
        # if the interval straddles two hydrophone recordings then move the start timestamp for saving
        else:
            if next_timestamp:
                if next_timestamp in exclusion_dict.keys():
                    next_exclusion_values = sorted(exclusion_dict[next_timestamp])
                    if (
                        (exclude_end / 1000 + timestamp - next_timestamp) / 1000
                    ) > next_exclusion_values[0][0]:
                        next_exclusion_values[0][0] = (
                            exclude_end / 1000 + timestamp - next_timestamp
                        ) / 1000
                        exclusion_dict[next_timestamp] = next_exclusion_values
                else:
                    exclusion_dict[next_timestamp] = [[exclude_end, -1]]
    # if there's no exlcusion interval just save the whole thing
    else:
        audio.export(
            os.path.join(
                OUT_ROOT,
                OUTPUT_PREFIX
                + NOISE_ID
                + "_"
                + str(timestamp)
                + "_"
                + str(int(timestamp * (len(audio) / 1000)))  # 10 minute intervals
                + OUTPUT_DATA_FORMAT,
            ),
            format=OUTPUT_DATA_FORMAT[1:],
        )

# TODO: parse each individual interval once we have better data
# TODO: simplify this code by loading (+/- audio files into memory too)
# TODO: make the following code more generalizeable to multiple deployments
# TODO: make this more modular
# TODO: add testing suite
