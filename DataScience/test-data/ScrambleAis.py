import uuid
import random
import pickle
import pandas as pd


def offset_data(ais):
    """Offsets lat and lon by random amount for each induvidual mmsi. Also changes ship mmsi into uuid

    Parameters
    ----------
    ais : pd.DataFrame()
        AIS position samples with ship type

    Returns
    -------
    scrambled_ais : pd.DataFrame()
        AIS position samples with ship type and counts, with locations and mmsis obfuscated

    """

    # Create Dict mapping for mmsi
    mmsi_offsets = {}
    rows = []

    for index, row in ais.iterrows():
        if row["mmsi"] not in mmsi_offsets:
            # Create new randomized identifier and coordinates
            id = uuid.uuid4()
            mmsi_offsets[row["mmsi"]] = {"uuid": id}
            lat, lon = random.uniform(-90, 90), random.uniform(-180, 180)
            lat_offset = lat - row["lat"]
            lon_offset = lon - row["lon"]
            mmsi_offsets[row["mmsi"]]["lat_offset"] = lat_offset
            mmsi_offsets[row["mmsi"]]["lon_offset"] = lon_offset
        else:
            # Read identifier from map
            id = mmsi_offsets[row["mmsi"]]["uuid"]
            # Calculate lat/lon from offset
            lat = mmsi_offsets[row["mmsi"]]["lat_offset"] + row["lat"]
            lon = mmsi_offsets[row["mmsi"]]["lon_offset"] + row["lon"]

        mmsis_uw = [mmsi_offsets[x]["uuid"].hex for x in row["mmsis_uw"]]
        mmsis_nuw = [mmsi_offsets[x]["uuid"].hex for x in row["mmsis_nuw"]]
        rows.append(
            [
                row["type"],
                row["repeat"],
                id.hex,
                row["status"],
                row["turn"],
                row["speed"],
                row["accuracy"],
                lon,
                lat,
                row["course"],
                row["heading"],
                row["second"],
                row["maneuver"],
                row["raim"],
                row["radio"],
                row["timestamp"],
                row["shiptype"],
                row["h"],
                row["distance"],
                row["shipcount_uw"],
                mmsis_uw,
                row["shipcount_nuw"],
                mmsis_nuw,
            ]
        )

    scrambled_ais = pd.DataFrame(rows, columns=ais.columns)
    return scrambled_ais


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
    allowed_ships = set()
    rows = []
    for index, row in ais.iterrows():
        mmsi = row["mmsi"]
        # Add mmsi to allowed ships if under the limit
        if len(allowed_ships) < shp_count:
            allowed_ships.add(mmsi)

        if mmsi in allowed_ships:
            rows.append(
                [
                    row["type"],
                    row["repeat"],
                    row["mmsi"],
                    row["status"],
                    row["turn"],
                    row["speed"],
                    row["accuracy"],
                    row["lon"],
                    row["lat"],
                    row["course"],
                    row["heading"],
                    row["second"],
                    row["maneuver"],
                    row["raim"],
                    row["radio"],
                    row["timestamp"],
                    row["shiptype"],
                    row["h"],
                    row["distance"],
                    row["shipcount_uw"],
                    row["mmsis_uw"],
                    row["shipcount_nuw"],
                    row["mmsis_nuw"],
                ]
            )

    trimmed_ais = pd.DataFrame(rows, columns=ais.columns)
    return trimmed_ais


def create_status_test_data(ais_test_data):
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

    mmsi_first = ais_test_data["mmsi"].iloc[0]

    single_ship_ais_data = ais_test_data[ais_test_data["mmsi"] == mmsi_first]

    new_rows = []
    status = random.choice(["AtAnchor", "Moored", "NotUnderCommand", "UnderWayUsingEngine"])

    for index, row in single_ship_ais_data.iterrows():
        if index % 5 == 0:
            status = random.choice(["AtAnchor", "Moored", "NotUnderCommand", "UnderWayUsingEngine"])

        new_rows.append(
            [
                row["type"],
                row["repeat"],
                row["mmsi"],
                status,
                row["turn"],
                row["speed"],
                row["accuracy"],
                row["lon"],
                row["lat"],
                row["course"],
                row["heading"],
                row["second"],
                row["maneuver"],
                row["raim"],
                row["radio"],
                row["timestamp"],
                row["shiptype"],
                row["h"],
                row["distance"],
                row["shipcount_uw"],
                row["mmsis_uw"],
                row["shipcount_nuw"],
                row["mmsis_nuw"],
            ]
        )
    forced_status_ais = pd.DataFrame(new_rows, columns=single_ship_ais_data.columns)
    return forced_status_ais

def write_pickle(path, object):
    """writes a file as a pickle.

   Parameters
   ----------
   path : str
       String of path to write pickle
   object : ~
       Object to write to pickle
   """

    with open(path, "wb") as f:
        pickle.dump(object, f)


data_home = "/Users/williamspear/Data/AISonobuoy"
ais_pickle_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais.pickle"
trimmed_pickle_path = f"{data_home}/aisonobuoy-pibuoy-v2/ais_test.pickle"
ais = pd.read_pickle(ais_pickle_path)

offset_ais = offset_data(ais)
trimmed_offset_ais = trim_ais_data(offset_ais)

write_pickle(trimmed_pickle_path, trimmed_offset_ais)
