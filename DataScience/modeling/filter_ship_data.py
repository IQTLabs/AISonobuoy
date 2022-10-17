# file handling
import os

# data manipulation
import numpy as np
from math import radians, cos, sin, asin, sqrt

# data formatting
import pandas as pd

# audio data manipulation
from pydub import AudioSegment

# data directory filepath
ROOT = "/home/achadda/SonobuoyData/aisonobuoy-pibuoy-v2"

# filters
DEPLOYMENTS_OF_INTEREST = ["v2-mk2-3"]
SHIPTYPE_OF_INTEREST = "Tug"
STATUS_OF_INTEREST = "UnderWayUsingEngine"
DISTANCE_THRESHOLD = 300

# hydrophone file name components
HYDROPHONE_DATA_DIR = "hydrophone"
HYDROPHONE_RECORDING_FILETYPE = ".flac"
HYDROPHONE_PREFIX = "pibuoy-v2-mk2-3-"
HYDROPHONE_POSTFIX = "-hydrophone.flac"

# outputs
OUT_ROOT = "/home/achadda/tugboat_dataset/tugboat"
OUTPUT_DATA_FORMAT = ".wav"
OUTPUT_PREFIX = "tugboat_"

# (lat, long)
CAPE_BUOY_LOCATION = (28.410868, -80.603866)
ANNAPOLIS_BUOY_LOCATION = (38.951455, -76.552497)

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

# TODO: make the following code more generalizeable to multiple deployments
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

# add human readable name + reformat w/ mmsi + NaN -> None
cape_shp_df = v2mk2_shp_df.copy()
v2mk2_shp_df = None  # free memory
cape_shp_df = cape_shp_df.transpose()
cape_shp_df["mmsi"] = cape_shp_df.index
cape_shp_df = cape_shp_df.where(pd.notnull(cape_shp_df), None)

# create output directories
os.makedirs(OUT_ROOT, exist_ok=True)

# isolate timestamp part of hydrophone recording filenames
hydrophone_files_ls = os.listdir(
    os.path.join(ROOT, DEPLOYMENTS_OF_INTEREST[0], HYDROPHONE_DATA_DIR)
)
hydrophone_timestamps_arr = np.array(
    [
        int(x.split("-")[4])
        for x in hydrophone_files_ls
        if x.endswith(HYDROPHONE_RECORDING_FILETYPE)
    ]
)

mmsi_of_interest = set(
    cape_latlon_cleaned.loc[cape_latlon_cleaned["shiptype"] == SHIPTYPE_OF_INTEREST][
        "mmsi"
    ].to_list()
)

# filter by recordings where the boat is <300m from buoy, only ships reporting underway,
# and of the type "Tug"
timestamp_of_interest = set(
    cape_latlon_cleaned.loc[
        (cape_latlon_cleaned["shipcount_uw"] == 1)
        & (cape_latlon_cleaned["relative_distance_meters"] <= DISTANCE_THRESHOLD)
        & (cape_latlon_cleaned["shiptype"] == SHIPTYPE_OF_INTEREST)
    ]["timestamp"].to_list()
)

# get subset of ship dataframe that is relevant
subset_of_interest = cape_shp_df[cape_shp_df.index.isin(list(mmsi_of_interest))][
    STATUS_OF_INTEREST
]

# iterate through intervals selected from ship json
for idx, val in subset_of_interest.iteritems():
    curr_mmsi = idx
    # iterate through interval in list of intervals
    for interval in val:
        # pull AIS record corresponding to interval
        if (
            interval[0] in timestamp_of_interest
            or interval[-1] in timestamp_of_interest
        ):
            # get the nearest file timestamp
            file_timestamp = hydrophone_timestamps_arr[
                hydrophone_timestamps_arr < int(interval[0])
            ].max()

            # filepath to save sinppet
            file_path = os.path.join(
                ROOT,
                DEPLOYMENTS_OF_INTEREST[0],
                HYDROPHONE_DATA_DIR,
                HYDROPHONE_PREFIX + str(file_timestamp) + HYDROPHONE_POSTFIX,
            )
            # load the entire audio recording from file
            audio = AudioSegment.from_file(
                file_path, format=HYDROPHONE_RECORDING_FILETYPE[1:]
            )
            # pull the interval in milliseconds
            audio_of_interest = audio[
                (int(interval[0]) - file_timestamp)
                * 1000 : (int(interval[-1]) - file_timestamp)
                * 1000
            ]
            # export the sinppet from the file
            audio_of_interest.export(
                os.path.join(
                    OUT_ROOT,
                    OUTPUT_PREFIX
                    + curr_mmsi
                    + "_"
                    + str(interval[0])
                    + "_"
                    + str(interval[-1])
                    + OUTPUT_DATA_FORMAT,
                ),
                format=OUTPUT_DATA_FORMAT[1:],
            )

# TODO: make this not ignore intervals that are between files (+/- audio files into memory too)
# TODO: make this script such that it can take differnt classes and extract their data
# TODO: modularize this script
# TODO: add "NotUnderCommand" status
# TODO: add testing suite
