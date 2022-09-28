# file handling
import os
import json

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
LOCATION_BUOY_LOCATION = (0, 0)

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
v2mk2_ais_df = pd.read_parquet(files_ls[0])
v2mk2_hmd_df = pd.read_parquet(files_ls[1])
v2mk2_shp_df = pd.read_json(files_ls[2], convert_dates=False, convert_axes=False)

location_ais = v2mk2_ais_df.copy()  # making human readable
v2mk2_ais_df = None  # free memory

# remove calibration artifacts w/ impossible lat/long
location_latlon_cleaned = location_ais.loc[
    (location_ais.lon != 181.0) & (location_ais.lat != 91.0)
].copy()

# add relative distance from buoy to each AIS entry
location_latlon_cleaned.loc[:, "relative_distance_meters"] = location_latlon_cleaned.apply(
    lambda row: distance_meters(
        LOCATION_BUOY_LOCATION[0], LOCATION_BUOY_LOCATION[1], row["lat"], row["lon"]
    ),
    axis=1,
)

# add human readable name + reformat w/ mmsi + NaN -> None
location_shp_df = v2mk2_shp_df.copy()
v2mk2_shp_df = None  # free memory
location_shp_df = location_shp_df.transpose()
location_shp_df["mmsi"] = location_shp_df.index
location_shp_df = location_shp_df.where(pd.notnull(location_shp_df), None)

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
    location_latlon_cleaned.loc[location_latlon_cleaned["shiptype"] == SHIPTYPE_OF_INTEREST][
        "mmsi"
    ].to_list()
)

# filter by recordings where the boat is <300m from buoy, only ships reporting underway, 
# and of the type "Tug"
timestamp_of_interest = set(
    location_latlon_cleaned.loc[
        (location_latlon_cleaned["shipcount_uw"] == 1)
        & (location_latlon_cleaned["relative_distance_meters"] <= DISTANCE_THRESHOLD)
        & (location_latlon_cleaned["shiptype"] == SHIPTYPE_OF_INTEREST)
    ]["timestamp"].to_list()
)

subset_of_interest = location_shp_df[location_shp_df.index.isin(list(mmsi_of_interest))][
    STATUS_OF_INTEREST
]

for idx, val in subset_of_interest.iteritems():
    curr_mmsi = idx
    for interval in val:
        if (
            interval[0] in timestamp_of_interest
            or interval[-1] in timestamp_of_interest
        ):
            file_timestamp = hydrophone_timestamps_arr[
                hydrophone_timestamps_arr < int(interval[0])
            ].max()

            file_path = os.path.join(
                ROOT,
                DEPLOYMENTS_OF_INTEREST[0],
                HYDROPHONE_DATA_DIR,
                HYDROPHONE_PREFIX + str(file_timestamp) + HYDROPHONE_POSTFIX,
            )
            audio = AudioSegment.from_file(
                file_path, format=HYDROPHONE_RECORDING_FILETYPE[1:]
            )
            audio_of_interest = audio[
                (int(interval[0]) - file_timestamp)
                * 1000 : (int(interval[-1]) - file_timestamp)
                * 1000
            ]
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

if __name__ == "__main__":
    # TODO: move to seperate file w/ pytest & add more tests
    assert not v2mk2_ais_df[["mmsi", "timestamp"]].duplicated().any()

    import json

    with open(files_ls[2], "r") as d:
        shp_dict = json.load(d)

    def check(shp):

        for mmsi in list(shp.keys()):
            seen = []
            for status in list(shp[mmsi].keys()):
                for interval in shp[mmsi][status]:
                    seen.append(interval[0])
                    seen.append(interval[1])
            assert len(set(seen)) == len(seen)
            break

    check(shp_dict)
