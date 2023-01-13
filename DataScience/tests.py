import json
import math
import os
from pathlib import Path

import miniaudio
import numpy as np
import pandas as pd
from pydub import AudioSegment
import pytest

import AisAudioLabeler as aal
import LabelerUtilities as lu


@pytest.fixture
def ais_fixed_data():
    ais_parquet_path = f"./test-data/v1-test/ais-fixed.parquet"
    ais = pd.read_parquet(ais_parquet_path)
    ## Parquet loads as array, while augment_ais_data returns a list. Conversion for assertion
    ais["mmsis_nuw"] = ais["mmsis_nuw"].apply(lambda x: x.tolist())
    ais["mmsis_uw"] = ais["mmsis_uw"].apply(lambda x: x.tolist())
    return ais


@pytest.fixture
def ais_test_data(data_home, source):
    ais = aal.get_ais_dataframe(data_home, source, force=True)
    return ais


@pytest.fixture
def ais_forced_status_test_data(data_home, source_forced_status):
    ais = aal.get_ais_dataframe(data_home, source_forced_status, force=True)
    return ais


@pytest.fixture
def hmd_test_data():
    # TODO: Consider adding force
    # Note: Requires installing ffprobe on Ubuntu in workflow
    hmd_parquet_path = f"./test-data/v1-test/hmd.parquet"
    hmd = pd.read_parquet(hmd_parquet_path)
    return hmd


@pytest.fixture
def shp_test_data():
    shp_json_path = f"./test-data/v1-test/shp.json"
    with open(shp_json_path, "r") as f:
        shp = json.load(f)
    return shp


@pytest.fixture
def collection_test_data():
    collection_path = f"./test-data/collection-ais.json"
    collection = lu.load_json_file(collection_path)
    return collection


@pytest.fixture
def source(collection_test_data):
    return collection_test_data["sources"][0]


@pytest.fixture
def source_forced_status(collection_test_data):
    return collection_test_data["sources"][1]


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
        self,
        source,
        hydrophone,
        ais_test_data,
        ais_fixed_data,
        hmd_test_data,
        shp_test_data,
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
        assert ais_fixed_data.loc[
            :, ~ais_fixed_data.columns.isin(["distance", "speed"])
        ].equals(ais.loc[:, ~ais.columns.isin(["distance", "speed"])])
        # Compare distance and speed using an absolute threshold
        # so that the threshold units are meaningful
        threshold = 1e-6
        assert np.allclose(ais_fixed_data["distance"], ais["distance"], atol=threshold)
        assert np.allclose(ais_fixed_data["speed"], ais["speed"], atol=threshold)
        assert hmd.equals(hmd_test_data)

    def test_augment_ais_data_status(
        self, source, hydrophone, ais_forced_status_test_data, hmd_test_data
    ):
        ais, _, shp = aal.augment_ais_data(
            source, hydrophone, ais_forced_status_test_data.copy(), hmd_test_data.copy()
        )

        for mmsi_group in ais.groupby(["mmsi"], sort=False):
            mmsi = mmsi_group[-1]["mmsi"].unique()
            assert mmsi.size == 1, "More than one MMSI found in group"

        assert (
            not ais[["mmsi", "timestamp"]].duplicated().any()
        ), "Multiple AIS records for the same mmsi + timestamp"

        shp_expected = {
            "17261435f7264540b3f640b0cb95b0b5": {
                "Moored": [
                    (1645746685, 1645746906),
                ],
                "AtAnchor": [
                    (1645746487, 1645746896),
                ],
                "UnderWayUsingEngine": [
                    (1645746418, 1645746455),
                    (1645746466, 1645746476),
                    (1645746585, 1645746595),
                    (1645746618, 1645746626),
                    (1645746999, 1645747026),
                    (1645747037, 1645747046),
                ],
                "NotUnderCommand": [],
            }
        }

        assert shp == shp_expected, "augment_ais_data_status() shp.json test failed"


class TestLabelerUtilities:
    def test_compute_PL_MSP_SL(self):

        r = 1000.0  # [m]
        assert lu.compute_PL(r) == 60.0

        # Sound speeds give theta_c_g = 0.5
        c_1 = 1500.0  # [m/s]
        c_2 = 1500.0 / math.cos(0.5)  # [m/s]

        # Depth gives r_cs = 1000 m and equal sperical and cylindrical
        # spreading
        z_b = 1000.0  # [m]

        assert lu.compute_PL(r, c_1=c_1, c_2=c_2, z_b=z_b) == 60.0

        samples = np.ones(10)

        S_dB_re_V_per_μPa = -180
        gain_dB = 60

        MSP, SPL = lu.compute_MSP(samples, S_dB_re_V_per_μPa, gain_dB)

        assert MSP == 10.0**12
        assert SPL == 120.0

        SL, _, _, _ = lu.compute_SL(
            samples, S_dB_re_V_per_μPa, gain_dB, r, c_1=c_1, c_2=c_2, z_b=z_b
        )

        assert SL == 180

    def test_FLAC_to_WAV_export(self):

        data_path = Path("test-data/aisonobuoy-pibuoy-v2/v2-mk2-3/hydrophone")

        # Read FLAC audio file using pydub
        flac_file = "pibuoy-v2-mk2-3-1645399051-hydrophone.flac"
        audio = AudioSegment.from_file(data_path / flac_file, "flac")

        # Write WAV audio file using pydub
        wav_file = flac_file.replace(".flac", ".wav")
        audio.export(data_path / wav_file, format="wav")

        # Read FLAC and WAV audio files using miniaudio
        flac_f32 = miniaudio.flac_read_file_f32(data_path / flac_file)
        wav_f32 = miniaudio.wav_read_file_f32(data_path / wav_file)

        assert np.array_equal(np.array(wav_f32.samples), np.array(flac_f32.samples))

        # Clean up
        os.remove(data_path / wav_file)
