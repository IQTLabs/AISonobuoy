import uuid
import random
import pandas as pd

def _offset_information(df):
    # Create unique id
    id = uuid.uuid4()

    # Get offset to random coordinate
    lat, lon = random.uniform(-90, 90), random.uniform(-180, 180)
    lat_offset = lat - df.iloc[0]["lat"]
    lon_offset = lon - df.iloc[0]["lon"]

    # Apply id and offset
    df = df.assign(mmsi=id)
    df["lat"] = df["lat"].apply(lambda x: x + lat_offset)
    df["lon"] = df["lon"].apply(lambda x: x + lon_offset)
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


def trim_ais_data(ais, shp_count=3):
    """Trim ais data down to specified number of ships, by order of appearance.

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type
    shp_count : int
        Number of ships to trim ais data down

    Returns
    -------
    trimmed_ais : pd.DataFrame()
        AIS position samples with ship type and counts, with extra ship positions removed

    """
    trimmed_ais = pd.DataFrame()
    grouped_ais = ais.groupby("mmsi")
    count = 0
    for group in grouped_ais:
        if count >= shp_count:
            break
        # Add ship to return value
        trimmed_ais = trimmed_ais.append(group[1])
        count += 1

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


data_home = "/Users/williamspear/Data/AISonobuoy"
ais_parquet_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais.parquet"
trimmed_parquet_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais_test.parquet"
ais = pd.read_parquet(ais_parquet_path)

offset_ais = scramble_data(ais)
trimmed_offset_ais = trim_ais_data(offset_ais)

write_parquet(trimmed_parquet_path, trimmed_offset_ais)
