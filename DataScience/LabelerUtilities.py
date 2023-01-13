import json
import logging
import math
from pathlib import Path
import subprocess

from matplotlib import pyplot as plt
import miniaudio
import numpy as np
import pandas as pd
from pydub import AudioSegment
from sklearn.cluster import KMeans
from sklearn_extra.cluster import KMedoids

import LabelerUtilities as lu

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

logger = logging.getLogger("LabelerUtilities")
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
    with open(inp_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data


def get_audio_file(inp_path):
    """Get audio segment from an audio file.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the audio file to open

    Returns
    -------
    audio : pydub.audio_segment.AudioSegment
        The audio segment

    See also:
        https://github.com/jiaaro/pydub

    """
    logger.info(f"Getting {inp_path}")
    if inp_path.suffix.lower() == ".wav":
        audio = AudioSegment.from_wav(inp_path)

    elif inp_path.suffix.lower() == ".flac":
        audio = AudioSegment.from_file(inp_path, "flac")

    return audio


def probe_audio_file(input_path):
    """Probe audio file to obtain stream entry values.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the audio file to probe

    Returns
    -------
    probe : dict
        Values of the audio stream entries

    See also:
        https://github.com/jiaaro/pydub

    """
    cp = subprocess.run(
        [
            "ffprobe",
            "-v",
            "error",
            "-select_streams",
            "a:0",
            "-show_entries",
            "stream=codec_name,codec_type,sample_rate,avg_frame_rate,duration",
            "-of",
            "json",
            str(input_path),
        ],
        capture_output=True,
    )
    probe = json.loads(cp.stdout)
    return probe["streams"][0]


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


def compute_source_metrics(source, vld_t, vld_lambda, vld_varphi, vld_h, hydrophone):
    """Compute the topocentric position and velocity of the source
    relative to the hydrophone, and corresponding heading, heading
    first derivative, distance, and speed.

    Parameters
    ----------
    source : dict
        The source configuration
    vld_t
        Time from start of track [s]
    vld_lambda
        Geodetic longitude [rad]
    vld_varphi
        Geodetic latitude [rad]
    vld_h
        Elevation [m]
    hydrophone : dict
        The hydrophone configuration

    Returns
    -------
    distance : numpy.ndarray
        Source distance from hydrophone [m]
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_dot : numpy.ndarray
        Source heading first derivative
    speed : numpy.ndarray
        Source speed [m/s]
    r_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]
    v_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) velocity [m/s]

    See:
        Montenbruck O., Gill E.; Satellite Orbits; Springer, Berlin (2001); pp. 37 and 188.

    """
    logger.info(
        f"Computing source {source['name']} metrics for hydrophone {Path(hydrophone['name'].lower()).stem}"
    )
    # Assign longitude, latitude, and elevation of hydrophone
    hyd_lambda = math.radians(hydrophone["lon"])
    hyd_varphi = math.radians(hydrophone["lat"])
    hyd_h = math.radians(hydrophone["ele"])

    # Compute the orthogonal transformation matrix from geocentric to
    # topocentric coordinates at hydrophone longitude, and latitude
    E = lu.compute_E(hyd_lambda, hyd_varphi)

    # Compute the geocentric position of the hydrophone, source, and
    # source relative to the hydrophone
    R_h = lu.compute_R(hyd_lambda, hyd_varphi, hyd_h)
    R_s = lu.compute_R(vld_lambda, vld_varphi, vld_h)
    R_s_h = R_s - np.atleast_2d(R_h).reshape(3, 1)

    # Compute the topocentric position and velocity of the source
    # relative to the origin, and corresponding heading, heading first
    # derivative, distance, and speed
    # TODO: Use instantaneous orthogonal transformation matrix?
    r_s_h = np.matmul(E, R_s_h)
    v_s_h = np.gradient(r_s_h, vld_t, axis=1)
    distance = np.sqrt(np.sum(np.square(r_s_h), axis=0))
    heading = 90 - np.degrees(np.arctan2(v_s_h[1, :], v_s_h[0, :]))
    heading_dot = np.abs(
        pd.DataFrame(np.gradient(heading, vld_t)).ewm(span=3).mean().to_numpy()
    ).flatten()
    speed = np.sqrt(np.sum(np.square(v_s_h), axis=0))
    return distance, heading, heading_dot, speed, r_s_h, v_s_h


def plot_source_metrics(
    source, hydrophone, heading, heading_dot, distance, speed, r_s_h
):
    """Plot source track, and histograms of source distance, heading,
    heading first derivative, and speed.

    Parameters
    ----------
    source : dict
        The source configuration
    hydrophone : dict
        The hydrophone configuration
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_dot : numpy.ndarray
        Source heading first derivative
    distance : numpy.ndarray
        Source distance from hydrophone [m]
    speed : numpy.ndarray
        Source speed [m/s]
    r_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]

    Returns
    -------
    None

    """
    logger.info(
        f"Plotting source {source['name']} metrics for hydrophone {Path(hydrophone['name'].lower()).stem}"
    )
    fig, axs = plt.subplots()
    axs.plot(r_s_h[0, :], r_s_h[1, :])
    axs.axhline(color="gray", linestyle="dotted")
    axs.axvline(color="gray", linestyle="dotted")
    axs.set_title("Track")
    axs.set_xlabel("east [m]")
    axs.set_ylabel("north [m]")
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(distance, bins=100)
    axs.set_title("Distance")
    axs.set_xlabel("distance [m]")
    axs.set_ylabel("counts")
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(90 - heading, bins=180)
    axs.set_title("Headings")
    axs.set_xlabel("heading [deg]")
    axs.set_ylabel("counts")
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(np.abs(heading_dot), bins=100)
    axs.set_title("Heading First Derivative")
    axs.set_xlabel("heading first derivative [deg/s]")
    axs.set_ylabel("counts")
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(speed, bins=100)
    axs.set_title("Speed")
    axs.set_xlabel("speed [m/s]")
    axs.set_ylabel("counts")
    plt.show()


def cluster_source_metrics(
    distance,
    distance_n_clusters,
    heading,
    heading_n_clusters,
    heading_dot,
    heading_dot_n_clusters,
    speed,
    speed_n_clusters,
):
    """Compute clusters of distance, heading, heading first derivative,
    and speed.

    Parameters
    ----------
    distance : numpy.ndarray
        Source distance from the hydrophone [m]
    distance_n_clusters : int
        Number of distance clusters
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive [deg]
    heading_n_clusters : int
        Number of heading clusters
    heading_dot : numpy.ndarray
        Source heading first derivative, zero at north, clockwise
        positive [deg/s]
    heading_dot_n_clusters : int
        Number of heading dot clusters
    speed : numpy.ndarray
        Source speed [m/s]
    speed_n_clusters : int
        Number of speed clusters

    Returns
    -------
    distance_clusters : sklearn.cluster.KMeans
        Fitted estimator for distance
    heading_clusters : sklearn.cluster.KMeans
        Fitted estimator for heading
    heading_dot_clusters : sklearn_extra.cluster.KMedoids
        Fitted estimator for heading first derivative
    speed_clusters : sklearn.cluster.KMeans
        Fitted estimator for speed

    """
    logger.info(f"Computing clusters of heading, distance, and speed")
    distance_clusters = KMeans(n_clusters=distance_n_clusters, random_state=0).fit(
        distance.reshape(-1, 1)
    )
    heading_clusters = KMeans(n_clusters=heading_n_clusters, random_state=0).fit(
        90 - heading.reshape(-1, 1)
    )
    heading_dot_clusters = KMedoids(
        n_clusters=heading_dot_n_clusters, random_state=0
    ).fit(heading_dot.reshape(-1, 1))
    speed_clusters = KMeans(n_clusters=speed_n_clusters, random_state=0).fit(
        speed.reshape(-1, 1)
    )
    return distance_clusters, heading_clusters, heading_dot_clusters, speed_clusters


def get_audio_samples(inp_path):
    """Get audio samples from an audio file.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the audio file to read

    Returns
    -------
    samples : numpy.ndarray
        The audio samples as 32 bits float

    See also:
        https://github.com/irmen/pyminiaudio

    """
    logger.info(f"Reading {inp_path}")
    if inp_path.suffix.lower() == ".wav":
        samples = miniaudio.wav_read_file_f32(inp_path).samples

    elif inp_path.suffix.lower() == ".flac":
        samples = miniaudio.flac_read_file_f32(inp_path).samples

    return np.array(samples)


def compute_PL(r, c_1=None, c_2=None, z_b=None):
    """Compute propagation loss assuming spherical spreading, unless
    ocean and bottom media sound speeds and depth are provided, then
    use cylindrical spreading.

    Parameters
    ----------
    r : float
        Range [m]
    c_1 : float
        Sound speed in the ocean [m/s]
    c_2 : float
        Sound speed in the bottom media [m/s]
    z_b : float
        Depth [m]

    Returns
    -------
    PL : float
        Propagation loss [dB re m²]

    """
    if z_b is None or c_1 is None or c_2 is None:
        # Assume spherical spreading
        PL = 20 * math.log10(r)  #  dB re m²

    else:
        # Assume cylindrical spreading
        theta_c_g = math.acos(c_1 / c_2)
        r_cs = z_b / (2 * theta_c_g)
        PL = 10 * math.log10(r_cs) + 10 * math.log10(r)

    return PL


def compute_MSP(samples, S_dB_re_V_per_μPa, gain_dB):
    """Use samples produced by a hydrophone to compute mean square
    pressure.

    Parameters
    ----------
    samples : numpy.ndarray
        The audio samples as 32 bits float
    S_dB_re_V_per_μPa : float
        Hydrophone sensitivity [dB re V/μPa]
    gain_dB : float
        Gain applied prior to analog to digital conversion [dB]

    Returns
    -------
    MSP : float
        Mean square pressure [μPa²]
    SPL : float
        Sound pressure level [dB re μPa²]

    """
    # Compute voltage at hydrophone
    gain = 10 ** (gain_dB / 20)
    voltage = samples / gain  # [V]

    # Compute pressure at hydrophone
    S_V_per_μPa = 10 ** (S_dB_re_V_per_μPa / 20)  # [V/μPa]
    pressure = voltage / S_V_per_μPa  # [μPa]

    # Compute mean square pressure and sound pressure level
    MSP = np.mean(np.power(pressure, 2))  # [μPa²]
    SPL = 10 * math.log10(MSP)  # [dB re μPa²]

    return MSP, SPL


def compute_SL(samples, S_dB_re_V_per_μPa, gain_dB, r, c_1=None, c_2=None, z_b=None):
    """Use samples produced by a hydrophone to compute source level.

    Parameters
    ----------
    samples : numpy.ndarray
        The audio samples as 32 bits float
    S_dB_re_V_per_μPa : float
        Hydrophone sensitivity [dB re V/μPa]
    gain_dB : float
        Gain applied prior to analog to digital conversion [dB]
    r : float
        Range [m]
    c_1 : float
        Sound speed in the ocean [m/s]
    c_2 : float
        Sound speed in the bottom media [m/s]
    z_b : float
        Depth [m]

    Returns
    -------
    SL : float
        Source level [dB re μPa²m²]
    PL : float
        Propagation loss [dB re m²]
    MSP : float
        Mean square pressure [μPa²]
    SPL : float
        Sound pressure level [dB re μPa²]

    """
    MSP, SPL = compute_MSP(samples, S_dB_re_V_per_μPa, gain_dB)
    PL = compute_PL(r, c_1=c_1, c_2=c_2, z_b=z_b)
    SL = SPL + PL  # [dB re μPa²m²]

    return SL, PL, MSP, SPL
