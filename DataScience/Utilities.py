import json
import logging
import math

import numpy as np
from pydub import AudioSegment


# WGS84 parameters
R_OPLUS = 6378137  # [m]
F_INV = 298.257223563

root_logger = logging.getLogger()
if not root_logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

logger = logging.getLogger("S3Utilities")
logger.setLevel(logging.INFO)


def load_json_file(inp_path):
    """Load a JSON file.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the JSON file to load

    Returns
    -------
    collection : object
        The object loaded

    """
    logger.info(f"Loading {inp_path}")
    with open(inp_path, "r") as f:
        data = json.load(f)
    return data


def get_wav_file(inp_path):
    """Get source audio from a WAV file.
    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the WAV file to open

    Returns
    -------
    audio : pydub.audio_segment.AudioSegment
        The audio segment

    See also:
    https://github.com/jiaaro/pydub
    """
    logger.info(f"Getting {inp_path}")
    audio = AudioSegment.from_wav(inp_path)
    return audio


def export_audio_clip(audio, start_t, stop_t, clip_filepath):
    """Export a clip from an audio segment.

    Parameters
    ----------
    audio : pydub.audio_segment.AudioSegment
        The audio segment
    start_t : int
        Start time of clip to export [ms]
    start_t : int
        Start time of clip to export [ms]
    clip_filepath : pathlib.Path()
        Path of the clip file to export

    Returns
    -------
    None
    """
    clip = audio[start_t:stop_t]
    clip.export(clip_filepath, format="wav")


def compute_E(_lambda, _varphi):
    """Compute geocentric east, north, and zenith unit vectors at a
    given geodetic longitude and latitude, and the corresponding
    orthogonal transformation matrix from geocentric to topocentric
    coordinates.

    Parameters
    ----------
    _lambda : float
        Geodetic longitude [rad]
    _varphi : float
        Geodetic latitude [rad]

    Returns
    -------
    E : numpy.ndarray
        Orthogonal transformation matrix from geocentric to
        topocentric coordinates
    """
    e_E = np.array([-math.sin(_lambda), math.cos(_lambda), 0])
    e_N = np.array(
        [
            -math.sin(_varphi) * math.cos(_lambda),
            -math.sin(_varphi) * math.sin(_lambda),
            math.cos(_varphi),
        ]
    )
    e_Z = np.array(
        [
            math.cos(_varphi) * math.cos(_lambda),
            math.cos(_varphi) * math.sin(_lambda),
            math.sin(_varphi),
        ]
    )
    E = np.row_stack((e_E, e_N, e_Z))
    return E


def compute_R(_lambda, _varphi, _h):
    """Compute the geocentric position given geodetic longitude and
    latitude, and elevation.

    Parameters
    ----------
    _lambda : float or numpy.ndarray
        Geodetic longitude [rad]
    _varphi : float or numpy.ndarray
        Geodetic latitude [rad]
    _h : float or numpy.ndarray
        Elevation [m]

    Returns
    -------
    R : numpy.ndarray
        Geocentric position [m]

    """
    f = 1 / F_INV
    if type(_lambda) == float:
        N = R_OPLUS / math.sqrt(1 - f * (2 - f) * math.sin(_varphi) ** 2)
        R = np.array(
            [
                (N + _h) * math.cos(_varphi) * math.cos(_lambda),
                (N + _h) * math.cos(_varphi) * math.sin(_lambda),
                ((1 - f) ** 2 * N + _h) * math.sin(_varphi),
            ]
        )
    elif type(_lambda) == np.ndarray:
        N = R_OPLUS / np.sqrt(1 - f * (2 - f) * np.sin(_varphi) ** 2)
        R = np.row_stack(
            (
                (N + _h) * np.cos(_varphi) * np.cos(_lambda),
                (N + _h) * np.cos(_varphi) * np.sin(_lambda),
                ((1 - f) ** 2 * N + _h) * np.sin(_varphi),
            ),
        )
    return R
