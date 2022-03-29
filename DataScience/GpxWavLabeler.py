from argparse import ArgumentParser
from datetime import datetime
import json
import logging
import math
from pathlib import Path

from lxml import etree
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd
from pydub import AudioSegment
from sklearn.cluster import KMeans


# WGS84 parameters
R_OPLUS = 6378137  # [m]
F_INV = 298.257223563

# Logging configuration
root = logging.getLogger()
if not root.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root.addHandler(ch)

logger = logging.getLogger("GpxWavLabeler")
logger.setLevel(logging.INFO)


def load_collection_json_file(inp_path):
    """Load collection JSON file.

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the JSON file to load

    Returns
    -------
    collection : dict
        The collection configuration

    """
    logger.info(f"Loading {inp_path}")
    with open(inp_path, "r") as f:
        collection = json.load(f)
    return collection


def parse_source_gpx_file(inp_path):
    """Parse a GPX file having the following structure:

    <gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" creator="Suunto app" version="1.1" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
      <metadata>
        <name></name>
        <desc/>
        <author>
          <name></name>
        </author>
      </metadata>
      <trk>
        <name></name>
        <trkseg>
          <trkpt lat="12.345678" lon="-23.456789">
            <ele>-3.4</ele>
            <time>2022-02-22T18:09:02Z</time>
            <extensions>
              <gpxtpx:TrackPointExtension>
                <gpxtpx:hr>95</gpxtpx:hr>
              </gpxtpx:TrackPointExtension>
            </extensions>
          </trkpt>
        </trkseg>
      </trk>
    </gpx>

    Parameters
    ----------
    inp_path : pathlib.Path()
        Path of the GPX file to parse

    Returns
    -------
    gpx : dict
        Track, track segments, and track points

    See also:
    https://en.wikipedia.org/wiki/GPS_Exchange_Format
    """
    logger.info(f"Parsing {inp_path}")
    # Parse input file
    parser = etree.XMLParser(remove_blank_text=True)
    tree = etree.parse(inp_path, parser)

    # Pretty print input file locally
    out_path = inp_path.with_name(inp_path.name.replace(".gpx", "-pretty.gpx"))
    tree.write(out_path, pretty_print=True)

    # Collect tracks
    root = tree.getroot()
    gpx = {}
    gpx["metadata"] = {}
    gpx["trks"] = []
    for trk_element in root.iter("{http://www.topografix.com/GPX/1/1}trk"):

        # Collect track segments
        trk = {}
        trk["name"] = trk_element.find("{http://www.topografix.com/GPX/1/1}name").text
        trk["trksegs"] = []
        for trkseg_element in root.iter("{http://www.topografix.com/GPX/1/1}trkseg"):

            # Collect track points
            trkseg = {}
            trkseg["lat"] = []
            trkseg["lon"] = []
            trkseg["ele"] = []
            trkseg["time"] = []
            start_time = None
            for trkpt_element in root.iter("{http://www.topografix.com/GPX/1/1}trkpt"):
                trkseg["lat"].append(
                    math.radians(float(trkpt_element.get("lat")))
                )  # [rad]
                trkseg["lon"].append(
                    math.radians(float(trkpt_element.get("lon")))
                )  # [rad]
                ele_element = trkpt_element.find(
                    "{http://www.topografix.com/GPX/1/1}ele"
                )
                if ele_element is not None:
                    trkseg["ele"].append(float(ele_element.text))  # [m]
                else:
                    trkseg["ele"].append(-R_OPLUS)

                time = datetime.fromisoformat(
                    trkpt_element.find("{http://www.topografix.com/GPX/1/1}time").text[
                        :-1
                    ]
                )
                if start_time is None:
                    start_time = time
                    trkseg["time"].append(0.0)
                else:
                    trkseg["time"].append((time - start_time).total_seconds())  # [s]

            trk["trksegs"].append(trkseg)

        gpx["trks"].append(trk)

    return gpx


def get_hydrophone_wav_file(inp_path):
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


def compute_source_metrics(source, gpx, hydrophone):
    """Compute the topocentric position and velocity of the source
    relative to the hydrophone, and corresponding heading, heading
    first derivative, distance, and speed.

    Parameters
    ----------
    source : dict
        The source configuration
    gpx : dict
        Track, track segments, and track points
    hydrophone : dict
        The hydrophone configuration

    Returns
    -------
    vld_t : numpy.ndarray
        Time from start of track [s]
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
    v_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) velocity [m/s]

    See:
    Montenbruck O., Gill E.; Satellite Orbits; Springer, Berlin (2001); pp. 37 and 38.
    """
    logger.info(
        f"Computing source {source['name']} metrics for hydrophone {Path(hydrophone['name'].lower()).stem}"
    )
    # Assign longitude, latitude, elevation, and time from start of
    # track
    # TODO: Check single track and track segment assumption
    _lambda = np.array(gpx["trks"][0]["trksegs"][0]["lon"])  # geodetic longitude [rad]
    _varphi = np.array(gpx["trks"][0]["trksegs"][0]["lat"])  # geodetic latitude [rad]
    _h = np.array(gpx["trks"][0]["trksegs"][0]["ele"])  # elevation [m]
    _t = np.array(gpx["trks"][0]["trksegs"][0]["time"])  # time from start of track [s]

    # Ignore points at which the elevation was not recorded
    vld_idx = np.logical_and(
        np.logical_and(source["start_t"] < _t, _t < source["stop_t"]), _h != -R_OPLUS
    )
    logger.info(f"Found {np.sum(vld_idx)} valid values out of all {_t.shape[0]} values")
    vld_lambda = _lambda[vld_idx]
    vld_varphi = _varphi[vld_idx]
    vld_h = _h[vld_idx]
    vld_t = _t[vld_idx]

    # Compute geocentric east, north, and zenith unit vectors at an
    # origin corresponding to the hydrophone longitude, latitude, and
    # elevation, and the corresponding orthogonal transformation
    # matrix from geocentric to topocentric coordinates
    hyd_lambda = math.radians(hydrophone["lon"])
    hyd_varphi = math.radians(hydrophone["lat"])
    hyd_h = math.radians(hydrophone["ele"])
    e_E = np.array([-math.sin(hyd_lambda), math.cos(hyd_lambda), 0])
    e_N = np.array(
        [
            -math.sin(hyd_varphi) * math.cos(hyd_lambda),
            -math.sin(hyd_varphi) * math.sin(hyd_lambda),
            math.cos(hyd_varphi),
        ]
    )
    e_Z = np.array(
        [
            math.cos(hyd_varphi) * math.cos(hyd_lambda),
            math.cos(hyd_varphi) * math.sin(hyd_lambda),
            math.sin(hyd_varphi),
        ]
    )
    E = np.row_stack((e_E, e_N, e_Z))

    # Compute the geocentric position of the hydrophone
    f = 1 / F_INV
    N_h = R_OPLUS / math.sqrt(1 - f * (2 - f) * math.sin(hyd_varphi) ** 2)
    R_h = np.array(
        [
            (N_h + hyd_h) * math.cos(hyd_varphi) * math.cos(hyd_lambda),
            (N_h + hyd_h) * math.cos(hyd_varphi) * math.sin(hyd_lambda),
            ((1 - f) ** 2 * N_h + hyd_h) * math.sin(hyd_varphi),
        ]
    )

    # Compute the geocentric position of the source
    N_s = R_OPLUS / np.sqrt(1 - f * (2 - f) * np.sin(vld_varphi) ** 2)
    R_s = np.row_stack(
        (
            (N_s + vld_h) * np.cos(vld_varphi) * np.cos(vld_lambda),
            (N_s + vld_h) * np.cos(vld_varphi) * np.sin(vld_lambda),
            ((1 - f) ** 2 * N_s + vld_h) * np.sin(vld_varphi),
        ),
    )

    # Compute the geocentric position of the source relative to the
    # hydrophone
    R_s_h = R_s - np.atleast_2d(R_h).reshape(3, 1)

    # Compute the topocentric position and velocity of the source
    # relative to the origin, and corresponding heading, heading first
    # derivative, distance, and speed
    # TODO: Use instantaneous orthogonal transformation matrix?
    r_s_h = np.matmul(E, R_s_h)
    v_s_h = np.gradient(r_s_h, vld_t, axis=1)
    heading = 90 - np.degrees(np.arctan2(v_s_h[1, :], v_s_h[0, :]))
    heading_dot = (
        pd.DataFrame(np.gradient(heading, vld_t)).ewm(span=3).mean().to_numpy()
    ).flatten()
    distance = np.sqrt(np.sum(np.square(r_s_h), axis=0))
    speed = np.sqrt(np.sum(np.square(v_s_h), axis=0))
    return vld_t, heading, heading_dot, distance, speed, r_s_h, v_s_h


def plot_source_metrics(
    source, hydrophone, heading, heading_dot, distance, speed, r_s_h
):
    """Plot source track, and histograms of source heading, distance, and speed.

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
    axs.set_title("Track")
    axs.set_xlabel("east [m]")
    axs.set_ylabel("north [m]")
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
    axs.hist(distance, bins=100)
    axs.set_title("Distance")
    axs.set_xlabel("distance [m]")
    axs.set_ylabel("counts")
    plt.show()

    fig, axs = plt.subplots()
    axs.hist(speed, bins=100)
    axs.set_title("Speed")
    axs.set_xlabel("speed [m/s]")
    axs.set_ylabel("counts")
    plt.show()


def kmeans_cluster_source_metrics(
    heading,
    heading_n_clusters,
    speed,
    speed_n_clusters,
):
    """Compute k-means clusters of heading, and speed.

    Parameters
    ----------
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_n_clusters : int
        Number of heading clusters
    speed : numpy.ndarray
        Source speed [m/s]
    speed_n_clusters : int
        Number of speed clusters

    Returns
    -------
    heading_kmeans : sklearn.cluster.KMeans
        Fitted estimator for heading
    speed_kmeans : sklearn.cluster.KMeans
        Fitted estimator for speed
    """
    logger.info(f"Computing k-means clusters of heading, distance, and speed")
    heading_kmeans = KMeans(n_clusters=heading_n_clusters, random_state=0).fit(
        90 - heading.reshape(-1, 1)
    )
    speed_kmeans = KMeans(n_clusters=speed_n_clusters, random_state=0).fit(
        speed.reshape(-1, 1)
    )
    return heading_kmeans, speed_kmeans


def slice_source_audio_by_cluster(
    hydrophone,
    audio,
    vld_t,
    r_s_o,
    heading_dot,
    heading_kmeans,
    speed_kmeans,
    delta_t_max,
    n_clips_max,
    clip_home,
    do_plot=True,
):
    """Slice source audio by cluster. Optionally plot source track and
    label the intersection of the heading and speed clusters.

    Parameters
    ----------
    hydrophone : dict
        The hydorphone configuration
    audio : pydub.audio_segment.AudioSegment
        The audio segment
    vld_t : numpy.ndarray
        Time from start of track [s]
    r_s_o : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]
    heading_dot : numpy.ndarray
        Source heading first derivative
    heading_kmeans : sklearn.cluster.KMeans
        Fitted estimator for heading
    speed_kmeans : sklearn.cluster.KMeans
        Fitted estimator for speed
    delta_t_max : float
        the maximum time delta between positions used to define a
        contiguous audio sample [s]
    n_clips_max : int
        the maximum number of clips exported in each segment
    clip_home : pathlib.Path()
        Home directory for clips

    Returns
    -------
    None
    """
    logger.info(f"Slicing source audio by heading, heading first derivative, distance, and speed clusters")
    # Assign cluster centers and ensure heading clusters pair
    heading_centers = heading_kmeans.cluster_centers_
    heading_n_clusters = len(heading_centers)

    if np.sum(heading_centers > 0) != np.sum(heading_centers < 0):
        raise Exception("Number of positive and negative heading centers must be equal")

    speed_centers = speed_kmeans.cluster_centers_
    speed_n_clusters = len(speed_centers)

    # Consider each positive heading cluster center
    hyd_name = Path(hydrophone["name"].lower()).stem
    hyd_start_t = hydrophone["start_t"] * 1000
    hyd_stop_t = hydrophone["stop_t"] * 1000
    for pos_hdg_idx in range(heading_n_clusters // 2):

        # Identify the corresponding negative heading cluster center,
        # that is, 180 degrees from the positive heading cluster
        # center
        neg_hdg_idx = np.argmin(
            np.abs(
                heading_centers[heading_centers > 0][pos_hdg_idx]
                - heading_centers[heading_centers < 0]
                - 180
            )
        )

        # Identify the heading values corresponding to the positive
        # and negative heading cluster centers
        pos_lbl_idx = np.argwhere(
            heading_centers == heading_centers[heading_centers > 0][pos_hdg_idx]
        )[0, 0]
        neg_lbl_idx = np.argwhere(
            heading_centers == heading_centers[heading_centers < 0][neg_hdg_idx]
        )[0, 0]
        pos_plt_idx = heading_kmeans.labels_ == pos_lbl_idx
        neg_plt_idx = heading_kmeans.labels_ == neg_lbl_idx

        # Consider a binary division of heading first derivative
        for isgreater in [True, False]:
            if isgreater:
                dot_plt_idx = np.abs(heading_dot) > 1.0
            else:
                dot_plt_idx = np.abs(heading_dot) < 1.0

            # Consider each speed cluster center
            for spd_lbl_idx in range(speed_n_clusters):

                # Identify the speed values corresponding to the speed
                # cluster center
                spd_plt_idx = speed_kmeans.labels_ == spd_lbl_idx

                # Identify valid time sets in which succusive times
                # and no more than the specified delta time
                dub_t = vld_t[(pos_plt_idx | neg_plt_idx) & dot_plt_idx & spd_plt_idx]
                dub_t_sets = np.split(
                    dub_t, np.where(np.diff(dub_t) > delta_t_max)[0] + 1
                )

                # Export the specified number of clips having at least
                # two valid times
                n_clips = 0
                for dub_t_set in dub_t_sets:
                    if dub_t_set.shape[0] > 2:
                        dub_start_t = int(dub_t_set[0] * 1000)
                        dub_stop_t = int(dub_t_set[-1] * 1000)
                        if dub_stop_t < hyd_start_t or hyd_stop_t < dub_start_t:
                            continue
                        else:
                            start_t = max(hyd_start_t, dub_start_t)
                            stop_t = min(hyd_stop_t, dub_stop_t)
                        n_clips += 1
                        clip = audio[start_t:stop_t]
                        wav_filename = "{:s}-{:d}-{:d}{:+.1f}{:+.1f}"
                        if isgreater:
                            wav_filename += "-greater"
                        else:
                            wav_filename += "-lesser"
                        wav_filename += "{:+.1f}.wav"
                        clip.export(
                            clip_home
                            / wav_filename.format(
                                hyd_name,
                                start_t,
                                stop_t,
                                heading_centers[pos_lbl_idx][0],
                                heading_centers[neg_lbl_idx][0],
                                speed_centers[spd_lbl_idx][0],
                            ),
                            format="wav",
                        )
                        if n_clips > n_clips_max:
                            break

                # Optionally plot the track and color points
                # corresponding to the current heading and speed
                # cluster centers
                if do_plot:
                    fig, axs = plt.subplots()
                    axs.plot(r_s_o[0, :], r_s_o[1, :])
                    axs.plot(
                        r_s_o[0, pos_plt_idx & dot_plt_idx & spd_plt_idx],
                        r_s_o[1, pos_plt_idx & dot_plt_idx & spd_plt_idx],
                        ".",
                    )
                    axs.plot(
                        r_s_o[0, neg_plt_idx & dot_plt_idx & spd_plt_idx],
                        r_s_o[1, neg_plt_idx & dot_plt_idx & spd_plt_idx],
                        ".",
                    )
                    title = "{:s}\nheadings = {:.1f}, {:.1f} deg"
                    if isgreater:
                        title += ", heading_dot > 1"
                    else:
                        title += ", heading_dot < 1"
                    title += ", speed = {:.1f} m/s"
                    axs.set_title(
                        title.format(
                            hyd_name,
                            heading_centers[pos_lbl_idx][0],
                            heading_centers[neg_lbl_idx][0],
                            speed_centers[spd_lbl_idx][0],
                        )
                    )
                    axs.set_xlabel("east [m]")
                    axs.set_ylabel("north [m]")
                    plt.show()


"""Demonstrate GpxWavLabeler module.
"""
if __name__ == "__main__":
    parser = ArgumentParser(description="Use GPX data to slice a WAV file")
    parser.add_argument(
        "-D",
        "--data-home",
        default=str(Path("~").expanduser() / "Data" / "AISonobuoy"),
        help="the directory containing GPX and WAV files",
    )
    parser.add_argument(
        "-c",
        "--json-filename",
        default="cape-exercises-2022-02-22T18-09-01Z-collection.json",
        help="the JSON filename to load",
    )
    parser.add_argument(
        "-g",
        "--gpx-filename",
        default="suuntoapp-Motorsports-2022-02-22T18-09-01Z-track.gpx",
        help="the GPX filename to parse",
    )
    parser.add_argument(
        "-w",
        "--wav-filename",
        default=None,
        help="the WAV filename to open",
    )
    parser.add_argument(
        "--heading-n-clusters",
        type=int,
        default=10,
        help="the number of heading cluster means",
    )
    parser.add_argument(
        "--distance-n-clusters",
        type=int,
        default=3,
        help="the number of distance cluster means",
    )
    parser.add_argument(
        "--speed-n-clusters",
        type=int,
        default=4,
        help="the number of speed cluster means",
    )
    parser.add_argument(
        "--delta-t-max",
        type=float,
        default=4.0,
        help="the maximum time delta between positions used to define a contiguous audio sample [s]",
    )
    parser.add_argument(
        "--n-clips-max",
        type=int,
        default=3,
        help="the maximum number of clips exported in each segment",
    )
    parser.add_argument(
        "-C",
        "--clip-home",
        default=str(Path("~").expanduser() / "Datasets" / "AISonobuoy"),
        help="the directory containing audio clip files",
    )
    args = parser.parse_args()

    json_path = Path(args.data_home) / args.json_filename
    collection = load_collection_json_file(json_path)

    gpx_path = Path(args.data_home) / args.gpx_filename
    gpx = parse_source_gpx_file(gpx_path)

    if args.wav_filename is None:
        wav_filenames = [d["name"] for d in collection["hydrophones"]]
    else:
        wav_filenames = [args.wav_filename]
    for wav_filename in wav_filenames:
        wav_path = Path(args.data_home) / wav_filename
        audio = get_hydrophone_wav_file(wav_path)

        source = collection["sources"][0]
        hydrophone = next(
            d for d in collection["hydrophones"] if d["name"] == wav_filename
        )

        (
            vld_t,
            heading,
            heading_dot,
            distance,
            speed,
            r_s_h,
            v_s_h,
        ) = compute_source_metrics(source, gpx, hydrophone)

        plot_source_metrics(source, hydrophone, heading, heading_dot, distance, speed, r_s_h)

        heading_kmeans, distance_kmeans, speed_kmeans = kmeans_cluster_source_metrics(
            heading,
            args.heading_n_clusters,
            distance,
            args.distance_n_clusters,
            speed,
            args.speed_n_clusters,
        )

        slice_source_audio_by_cluster(
            hydrophone,
            audio,
            vld_t,
            r_s_o,
            heading_dot,
            heading_kmeans,
            speed_kmeans,
            args.delta_t_max,
            args.n_clips_max,
            Path(args.clip_home),
        )
