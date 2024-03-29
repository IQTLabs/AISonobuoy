import uuid
import random
import json
import os
import pandas as pd

def _offset_information(df):
    # Create unique id
    id = str(uuid.uuid4())

    # Get offset to random coordinate
    lat, lon = random.uniform(-90, 90), random.uniform(-180, 180)
    lat_offset = lat - df.iloc[0]["lat"]
    lon_offset = lon - df.iloc[0]["lon"]

    # Apply id and offset
    df = df.assign(mmsi=id)
    df["lat"] = df["lat"] + lat_offset
    df["lon"] = df["lon"] + lon_offset
    return df

def scramble_data(ais):
    """Offsets lat and lon by random amount for each individual mmsi. Also changes ship mmsi into uuid

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type

    Returns
    -------
    scrambled_ais : pd.DataFrame()
        AIS position samples with ship type and counts, with locations and mmsis obfuscated

    """

    ais_scrambled = ais.groupby("mmsi").apply(_offset_information)

    return ais_scrambled


def trim_ais_data(ais, group_len=100):
    """Trim ais data down by number of entries per ship.

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type
    group_len : int
        Cutoff for ship rows

    Returns
    -------
    trimmed_ais : pd.DataFrame()
        AIS position samples with ship type and counts, with extra ship positions removed

    """
    trimmed_ais = ais.groupby("mmsi").filter(lambda x: len(x) < group_len)

    return trimmed_ais


def create_status_test_data(ais):
    """Trim ais data to single ship and creates randomized status.

    Parameters
    ----------
    ais_test_data : pd.DataFrame()
        AIS position samples with ship type

    Returns
    -------
    forced_status_ais : pd.DataFrame()
        AIS dataframe with more varied statuses
    """

    mmsi_first = ais["mmsi"].iloc[0]

    single_ship_ais_data = ais.groupby('mmsi').get_group(mmsi_first)
    single_ship_ais_data["status"] = single_ship_ais_data["status"].apply(lambda x: random.choice(["AtAnchor", "Moored", "NotUnderCommand", "UnderWayUsingEngine"]))

    return single_ship_ais_data

def write_parquet(path, df):
    """writes a file as a parquet.

   Parameters
   ----------
   path : str
       String of path to write parquet
   df : ~
       Pandas Dataframe to write to parquet
   """

    df.to_parquet(path)


def split_parquet(inpath, outpath):
    """takes a parquet file and writes a file with split json. Note that this is not a true json file - each line is its own dict.

   Parameters
   ----------
   inpath : str
       String of path to read parquet
   outpath : str
       String of path to write parquet
   """
    df = pd.read_parquet(inpath)
    for _, row in df.iterrows():
        d = {
            "type": row["type"],
            "repeat": row["repeat"],
            "mmsi": row["mmsi"],
            "status": row["status"],
            "turn": row["turn"],
            "speed": row["speed"],
            "accuracy": row["accuracy"],
            "lon": row["lon"],
            "lat": row["lat"],
            "course": row["course"],
            "heading": row["heading"],
            "second": row["second"],
            "maneuver": row["maneuver"],
            "raim": row["raim"],
            "radio": row["radio"],
            "timestamp": row["timestamp"],
        }
        with open(outpath, 'a') as fp:
            json.dump(d, fp)
            fp.write("\n")


def main():
    data_home = f"{os.path.expanduser('~')}/Data/AISonobuoy"
    ais_parquet_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais.parquet"
    trimmed_parquet_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais-test.parquet"
    split_ais_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais-test.json"
    ais = pd.read_parquet(ais_parquet_path)

    offset_ais = scramble_data(ais)
    trimmed_offset_ais = trim_ais_data(offset_ais)

    write_parquet(trimmed_parquet_path, trimmed_offset_ais)
    split_parquet(trimmed_parquet_path, split_ais_path)

if __name__ == "__main__":
    main()
