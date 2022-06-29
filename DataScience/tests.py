import pytest
import os
import json
import pandas as pd
import LabelerUtilities as lu
import AisAudioLabeler as aal
from pathlib import Path


@pytest.fixture
def ais_test_data():
    ais_parquet_path = f"{os.getcwd()}/test-data/v1-test/ais.parquet"
    ais = pd.read_parquet(ais_parquet_path)
    return ais


@pytest.fixture
def ais_forced_status_test_data():
    ais_parquet_path = f"{os.getcwd()}/test-data/v1-test/forced_status_ais.parquet"
    ais = pd.read_parquet(ais_parquet_path)
    return ais


@pytest.fixture
def hmd_test_data():
    hmd_parquet_path = f"{os.getcwd()}/test-data/v1-test/hmd.parquet"
    hmd = pd.read_parquet(hmd_parquet_path)
    return hmd


@pytest.fixture
def shp_test_data():
    shp_json_path = f"{os.getcwd()}/test-data/v1-test/shp.json"
    with open(shp_json_path, "r") as f:
        shp = json.load(f)
    return shp


@pytest.fixture
def collection_test_data():
    collection_path = f"{os.getcwd()}/test-data/collection-ais.json"
    collection = lu.load_json_file(collection_path)
    return collection


@pytest.fixture
def source(collection_test_data):
    return collection_test_data["sources"][0]


@pytest.fixture
def hydrophone(collection_test_data):
    return collection_test_data["hydrophones"][0]


@pytest.fixture
def data_home():
    return Path(os.getcwd())


class TestAisAudioLabeler:
    def test_get_ais_dataframe(self, ais_test_data, data_home, source):
        ais = aal.get_ais_dataframe(data_home, source)
        assert ais.equals(ais_test_data)

    def test_get_shp_dictionary(self, shp_test_data, data_home, source):
        shp = aal.get_shp_dictionary(data_home, source)
        assert shp == shp_test_data

    def test_get_hmd_dataframe(self, hmd_test_data, data_home, hydrophone):
        hmd = aal.get_hmd_dataframe(data_home, hydrophone)
        assert hmd.equals(hmd_test_data)

    def test_augment_ais_data_consistency(
        self, source, hydrophone, ais_test_data, hmd_test_data, shp_test_data
    ):
        ais, hmd, _shp = aal.augment_ais_data(
            source, hydrophone, ais_test_data.copy(), hmd_test_data.copy()
        )

        # TODO: Understand why this is needed: int64 conversion?
        with open("test-data/_shp.json", "w") as f:
            json.dump(_shp, f)
        with open("test-data/_shp.json", "r") as f:
            shp = json.load(f)

        assert shp == shp_test_data
        assert ais.equals(ais_test_data)
        assert hmd.equals(hmd_test_data)

    def test_augment_ais_data_status(
        self, source, hydrophone, ais_forced_status_test_data, hmd_test_data
    ):
        ais, hmd, shp = aal.augment_ais_data(
            source, hydrophone, ais_forced_status_test_data.copy(), hmd_test_data.copy()
        )
        shp_expected = {
            "17261435f7264540b3f640b0cb95b0b5": {
                "Moored": [
                    (1645543046, 1645543046),
                    (1645545747, 1645545747),
                    (1645682727, 1645682727),
                    (1645734026, 1645734026),
                    (1645746685, 1645746906),
                ],
                "AtAnchor": [
                    (1645547005, 1645547005),
                    (1645548445, 1645548445),
                    (1645550608, 1645550608),
                    (1645550965, 1645550965),
                    (1645556007, 1645556007),
                    (1645630348, 1645630348),
                    (1645746487, 1645746896),
                ],
                "UnderWayUsingEngine": [
                    (1645558526, 1645558526),
                    (1645683629, 1645683629),
                    (1645721245, 1645721245),
                    (1645725567, 1645725567),
                    (1645727726, 1645727726),
                    (1645733846, 1645733846),
                    (1645737449, 1645737449),
                    (1645745516, 1645745516),
                    (1645746418, 1645746455),
                    (1645746466, 1645746476),
                    (1645746585, 1645746595),
                    (1645746607, 1645746607),
                    (1645746618, 1645746626),
                    (1645746999, 1645747026),
                    (1645747037, 1645747046),
                ],
                "NotUnderCommand": [(1645559247, 1645559247), (1645746926, 1645746926)],
            }
        }

        assert shp == shp_expected
