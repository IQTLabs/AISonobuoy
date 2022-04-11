from argparse import ArgumentParser
from datetime import datetime
import logging
import math
from pathlib import Path
import time

from lxml import etree
from matplotlib import pyplot as plt
import numpy as np
import pandas as pd

import LabelerUtilities as lu

# WGS84 parameters
R_OPLUS = 6378137  # [m]
F_INV = 298.257223563

# Logging configuration
root_logger = logging.getLogger()
if not root_logger.handlers:
    ch = logging.StreamHandler()
    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    ch.setFormatter(formatter)
    root_logger.addHandler(ch)

logger = logging.getLogger("GpxAudioLabeler")
logger.setLevel(logging.INFO)


def parse_source_gpx_file(inp_path, source):
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
    source : dict
        The source configuration

    Returns
    -------
    gpx : dict
        Track, track segments, and track points
    vld_t
        Time from start of track [s]
    vld_lambda
        Geodetic longitude [rad]
    vld_varphi
        Geodetic latitude [rad]
    vld_h
        Elevation [m]

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
            for trkpt_element in trkseg_element.iter(
                "{http://www.topografix.com/GPX/1/1}trkpt"
            ):
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

                cur_time = datetime.fromisoformat(
                    trkpt_element.find("{http://www.topografix.com/GPX/1/1}time").text[
                        :-1
                    ]
                )
                if start_time is None:
                    start_time = cur_time
                    trkseg["time"].append(0.0)
                else:
                    trkseg["time"].append(
                        (cur_time - start_time).total_seconds()
                    )  # [s]

            trk["trksegs"].append(trkseg)

        gpx["trks"].append(trk)

        # Assign longitude, latitude, elevation, and time from start of
        # track
        # TODO: Check single track and track segment assumption
        _t = np.array(
            gpx["trks"][0]["trksegs"][0]["time"]
        )  # time from start of track [s]
        _lambda = np.array(
            gpx["trks"][0]["trksegs"][0]["lon"]
        )  # geodetic longitude [rad]
        _varphi = np.array(
            gpx["trks"][0]["trksegs"][0]["lat"]
        )  # geodetic latitude [rad]
        _h = np.array(gpx["trks"][0]["trksegs"][0]["ele"])  # elevation [m]

        # Ignore points at which the elevation was not recorded
        vld_idx = np.logical_and(
            np.logical_and(source["start_t"] < _t, _t < source["stop_t"]),
            _h != -R_OPLUS,
        )
        logger.info(
            f"Found {np.sum(vld_idx)} valid values out of all {_t.shape[0]} values"
        )
        vld_t = _t[vld_idx]
        vld_lambda = _lambda[vld_idx]
        vld_varphi = _varphi[vld_idx]
        vld_h = _h[vld_idx]

    return gpx, vld_t, vld_lambda, vld_varphi, vld_h


def slice_source_audio_by_cluster(
    hydrophone,
    audio,
    hyd_max_start_t,
    hyd_min_stop_t,
    vld_t,
    r_s_h,
    distance_clusters,
    heading_clusters,
    heading_dot_clusters,
    speed_clusters,
    delta_t_max,
    n_clips_max,
    clip_home,
    do_plot=True,
):
    """Slice source audio by heading, heading first derivative,
    distance, and speed clusters. Optionally plot source track and
    label the intersection of the heading, heading first derivative,
    distance, and speed clusters.

    Parameters
    ----------
    hydrophone : dict
        The hydrophone configuration
    audio : pydub.audio_segment.AudioSegment
        The audio segment
    hyd_max_start_t : int
       Maximum start_t of all hydrophones [ms]
    hyd_min_stop_t : int
       Minimum stop_t of all hydrophones [ms]
    vld_t : numpy.ndarray
        Time from start of track [s]
    r_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]
    distance_clusters : sklearn.cluster.KMeans
        Fitted estimator for distance
    heading_clusters : sklearn.cluster.KMeans
        Fitted estimator for heading
    heading_dot_clusters : sklearn_extra.cluster.KMedoids
        Fitted estimator for heading first derivative
    speed_clusters : sklearn.cluster.KMeans
        Fitted estimator for speed
    delta_t_max : float
        the maximum time delta between positions used to define a
        contiguous audio sample [s]
    n_clips_max : int
        the maximum number of clips exported in each segment
    clip_home : pathlib.Path()
        Home directory for clip files

    Returns
    -------
    None
    """
    logger.info(
        f"Slicing source audio by heading, heading first derivative, distance, and speed clusters"
    )
    # Identify hydrophone attributes
    hyd_name = Path(hydrophone["name"].lower()).stem

    # Assign cluster centers and ensure heading clusters pair
    distance_centers = distance_clusters.cluster_centers_
    distance_n_clusters = len(distance_centers)

    heading_centers = heading_clusters.cluster_centers_
    heading_n_clusters = len(heading_centers)

    if np.sum(heading_centers > 0) != np.sum(heading_centers < 0):
        raise Exception("Number of positive and negative heading centers must be equal")

    heading_dot_centers = heading_dot_clusters.cluster_centers_
    heading_dot_n_clusters = len(heading_dot_centers)

    speed_centers = speed_clusters.cluster_centers_
    speed_n_clusters = len(speed_centers)

    # Consider each distance cluster center
    for dis_lbl_idx in range(distance_n_clusters):

        # Identify the distance values corresponding to the distance
        # cluster center
        dis_plt_idx = distance_clusters.labels_ == dis_lbl_idx

        # Consider each positive heading cluster center
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
            pos_plt_idx = heading_clusters.labels_ == pos_lbl_idx
            neg_plt_idx = heading_clusters.labels_ == neg_lbl_idx

            # Consider each heading first derivative cluster center
            for dot_lbl_idx in range(heading_dot_n_clusters):

                # Identify the heading first derivative values corresponding to
                # the heading first derivative cluster center
                dot_plt_idx = heading_dot_clusters.labels_ == dot_lbl_idx

                # Consider each speed cluster center
                for spd_lbl_idx in range(speed_n_clusters):

                    # Identify the speed values corresponding to the
                    # speed cluster center
                    spd_plt_idx = speed_clusters.labels_ == spd_lbl_idx

                    # Identify valid time sets in which successive
                    # times and no more than the specified delta time
                    dub_t = vld_t[
                        (pos_plt_idx | neg_plt_idx)
                        & dot_plt_idx
                        & spd_plt_idx
                        & dis_plt_idx
                    ]
                    dub_t_sets = np.split(
                        dub_t, np.where(np.diff(dub_t) > delta_t_max)[0] + 1
                    )

                    # Export the specified number of clips having at
                    # least two valid times
                    n_clips = 0
                    for dub_t_set in dub_t_sets:
                        if dub_t_set.shape[0] > 2:
                            dub_start_t = int(dub_t_set[0] * 1000)
                            dub_stop_t = int(dub_t_set[-1] * 1000)
                            if (
                                dub_stop_t < hyd_max_start_t
                                or hyd_min_stop_t < dub_start_t
                            ):
                                continue
                            start_t = max(hyd_max_start_t, dub_start_t)
                            stop_t = min(hyd_min_stop_t, dub_stop_t)
                            n_clips += 1
                            wav_filename = (
                                "{:s}-{:d}-{:d}{:+.1f}{:+.1f}{:+.1f}{:+.1f}{:+.1f}.wav"
                            )
                            lu.export_audio_clip(
                                audio,
                                start_t,
                                stop_t,
                                clip_home
                                / wav_filename.format(
                                    hyd_name,
                                    start_t,
                                    stop_t,
                                    distance_centers[dis_lbl_idx][0],
                                    heading_centers[pos_lbl_idx][0],
                                    heading_centers[neg_lbl_idx][0],
                                    heading_dot_centers[dot_lbl_idx][0],
                                    speed_centers[spd_lbl_idx][0],
                                ),
                            )
                            if n_clips > n_clips_max:
                                break

                    # Optionally plot the track and color points
                    # corresponding to the current heading, heading
                    # first derivative, distance, and speed cluster
                    # centers
                    if do_plot:
                        fig, axs = plt.subplots()
                        axs.plot(r_s_h[0, :], r_s_h[1, :])
                        axs.plot(
                            r_s_h[
                                0, dis_plt_idx & pos_plt_idx & dot_plt_idx & spd_plt_idx
                            ],
                            r_s_h[
                                1, dis_plt_idx & pos_plt_idx & dot_plt_idx & spd_plt_idx
                            ],
                            ".",
                        )
                        axs.plot(
                            r_s_h[
                                0, dis_plt_idx & neg_plt_idx & dot_plt_idx & spd_plt_idx
                            ],
                            r_s_h[
                                1, dis_plt_idx & neg_plt_idx & dot_plt_idx & spd_plt_idx
                            ],
                            ".",
                        )
                        axs.axhline(color="gray", linestyle="dotted")
                        axs.axvline(color="gray", linestyle="dotted")
                        title = "{:s}\n"
                        title += "dis = {:.1f} m"
                        title += ", hdgs = {:.1f}, {:.1f} deg"
                        title += ", hdg dot = {:.1f} deg/s"
                        title += ", spd = {:.1f} m/s"
                        axs.set_title(
                            title.format(
                                hyd_name,
                                distance_centers[dis_lbl_idx][0],
                                heading_centers[pos_lbl_idx][0],
                                heading_centers[neg_lbl_idx][0],
                                heading_dot_centers[dot_lbl_idx][0],
                                speed_centers[spd_lbl_idx][0],
                            )
                        )
                        axs.set_xlabel("east [m]")
                        axs.set_ylabel("north [m]")
                        plt.show()
                        time.sleep(1)


def slice_source_audio_by_condition(
    hydrophone,
    audio,
    hyd_max_start_t,
    hyd_min_stop_t,
    vld_t,
    r_s_h,
    distance,
    distance_limits,
    heading,
    heading_limits,
    heading_dot,
    heading_dot_limits,
    speed,
    speed_limits,
    delta_t_max,
    n_clips_max,
    clip_home,
    do_plot=True,
):
    """Slice source audio by heading, heading first derivative,
    distance, and speed limits. Optionally plot source track and
    label the intersection of the heading, heading first derivative,
    distance, and speed clusters.

    Parameters
    ----------
    hydrophone : dict
        The hydrophone configuration
    audio : pydub.audio_segment.AudioSegment
        The audio segment
    hyd_max_start_t : int
       Maximum start_t of all hydrophones [ms]
    hyd_min_stop_t : int
       Minimum stop_t of all hydrophones [ms]
    vld_t : numpy.ndarray
        Time from start of track [s]
    r_s_h : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]
    distance : numpy.ndarray
        Source distance from hydrophone [m]
    distance_limits : [float]
        Distance limits
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_limits : [float]
        Heading limits
    heading_dot : numpy.ndarray
        Source heading first derivative
    heading_dot_limits : [float]
        Heading first derivative limits
    speed : numpy.ndarray
        Source speed [m/s]
    speed_limits : [float]
        Speed limits
    delta_t_max : float
        the maximum time delta between positions used to define a
        contiguous audio sample [s]
    n_clips_max : int
        the maximum number of clips exported in each segment
    clip_home : pathlib.Path()
        Home directory for clip files

    Returns
    -------
    None
    """
    logger.info(
        f"Slicing source audio by heading, heading first derivative, distance, and speed limits"
    )
    # Identify hydrophone attributes
    hyd_name = Path(hydrophone["name"].lower()).stem

    # Identify the distance values corresponding to the distance
    # limits
    dis_plt_idx = np.logical_and(
        distance_limits[0] < distance, distance < distance_limits[1]
    )

    # Identify the heading values corresponding to the heading limits
    hdg_plt_idx = np.logical_or(
        np.logical_and(heading_limits[0] < heading, heading < heading_limits[1]),
        np.logical_and(heading_limits[2] < heading, heading < heading_limits[3]),
    )

    # Identify the heading first derivative values corresponding to
    # the heading first derivative limits
    dot_plt_idx = np.logical_and(
        heading_dot_limits[0] < heading_dot, heading_dot < heading_dot_limits[1]
    )

    # Identify the speed values corresponding to the speed limits
    spd_plt_idx = np.logical_and(speed_limits[0] < speed, speed < speed_limits[1])

    # Identify valid time sets in which successive times and no more
    # than the specified delta time
    dub_t = vld_t[dis_plt_idx & hdg_plt_idx & dot_plt_idx & spd_plt_idx]
    dub_t_sets = np.split(dub_t, np.where(np.diff(dub_t) > delta_t_max)[0] + 1)

    # Export the specified number of clips having at least two valid
    # times
    n_clips = 0
    for dub_t_set in dub_t_sets:
        if dub_t_set.shape[0] > 2:
            dub_start_t = int(dub_t_set[0] * 1000)
            dub_stop_t = int(dub_t_set[-1] * 1000)
            if dub_stop_t < hyd_max_start_t or hyd_min_stop_t < dub_start_t:
                continue
            start_t = max(hyd_max_start_t, dub_start_t)
            stop_t = min(hyd_min_stop_t, dub_stop_t)
            n_clips += 1
            wav_filename = "{:s}-{:d}-{:d}-{:+.1f}to{:+.1f}-{:+.1f}to{:+.1f}-and-{:+.1f}to{:+.1f}-{:+.1f}to{:+.1f}-{:+.1f}to{:+.1f}.wav"
            lu.export_audio_clip(
                audio,
                start_t,
                stop_t,
                clip_home
                / wav_filename.format(
                    hyd_name,
                    start_t,
                    stop_t,
                    distance_limits[0],
                    distance_limits[1],
                    heading_limits[0],
                    heading_limits[1],
                    heading_limits[2],
                    heading_limits[3],
                    heading_dot_limits[0],
                    heading_dot_limits[1],
                    speed_limits[0],
                    speed_limits[1],
                ),
            )
            if n_clips > n_clips_max:
                break

    # Optionally plot the track and color points corresponding to the
    # current heading, heading first derivative, distance, and speed
    # cluster centers
    if do_plot:
        fig, axs = plt.subplots()
        axs.plot(r_s_h[0, :], r_s_h[1, :])
        axs.plot(
            r_s_h[0, dis_plt_idx & hdg_plt_idx & dot_plt_idx & spd_plt_idx],
            r_s_h[1, dis_plt_idx & hdg_plt_idx & dot_plt_idx & spd_plt_idx],
            ".",
        )
        axs.axhline(color="gray", linestyle="dotted")
        axs.axvline(color="gray", linestyle="dotted")
        title = "{:s}\n"
        title += "dis = {:.1f} to {:.1f} m"
        title += ", hdg = {:.1f} to {:.1f} and {:.1f} to {:.1f} deg"
        title += ", hdg dot = {:.1f} to {:.1f} deg/s"
        title += ", spd = {:.1f} to {:.1f} m/s"
        axs.set_title(
            title.format(
                hyd_name,
                distance_limits[0],
                distance_limits[1],
                heading_limits[0],
                heading_limits[1],
                heading_limits[2],
                heading_limits[3],
                heading_dot_limits[0],
                heading_dot_limits[1],
                speed_limits[0],
                speed_limits[1],
            )
        )
        axs.set_xlabel("east [m]")
        axs.set_ylabel("north [m]")
        plt.show()
        time.sleep(1)


def main():
    """Provide a command-line interface for the GpxAudioLabeler module."""
    parser = ArgumentParser(description="Use GPX data to slice a WAV file")
    parser.add_argument(
        "-D",
        "--data-home",
        default=str(Path("~").expanduser() / "Data" / "AISonobuoy"),
        help="the directory containing all GPX, WAV, and JSON files",
    )
    parser.add_argument(
        "-c",
        "--collection-filename",
        default="collection-gpx.json",
        help="the path of the collection JSON file to load",
    )
    """
    The sample JSON document contains entries in the following format
    which describe the method, and its parameters, used in creating
    labeled samples from the collection. The method can be either
    "clusters" or "conditionals".

    If "clusters", the samples are all placed in the specified output
    directory, and labeled with the start and stop times, and the
    distance, heading, heading rate, and speed cluster averages.

    If "conditionals", the samples are all placed in the output
    directory and labeled with the start and stop times, and the
    distance, heading, heading rate, and speed limits. Multiple
    entries with the "conditionals" method will result in samples in a
    set of labeled directories.

    The maximum time delta between positions used to define a
    contiguous audio sample is in seconds.

    Format:
    [
        {
            "name": "default",
            "method": {
                "type": "clusters",
                "distance_n_clusters": 3,
                "heading_n_clusters": 10,
                "heading_dot_n_clusters": 2,
                "speed_n_clusters": 4
            },
            "delta_t_max": 4.0,
            "n_clips_max": 3,
            "output_dir": "default"
        },
        {
            "name": "close-north-stable-fast",
            "method": {
                "type": "conditionals",
                "distance_limits": [0, 250],
                "heading_limits": [-10, 0, 0, 10],
                "heading_dot_limits": [0, 1],
                "speed_limits": [10, 20]
            },
            "delta_t_max": 4.0,
            "n_clips_max": 3,
            "output_dir": "close-north-stable-fast"
        }
    ]
    """
    parser.add_argument(
        "-s",
        "--sampling-filepath",
        default=str(Path(__file__).parent / "data" / "sampling-gpx.json"),
        help="the path of the sampling JSON file to process",
    )
    parser.add_argument(
        "-p",
        "--do-plot-clips",
        action="store_true",
        help="do plot track with identified clips",
    )
    parser.add_argument(
        "-P",
        "--do-plot-metrics",
        action="store_true",
        help="do plot track with computed metrics",
    )
    parser.add_argument(
        "-C",
        "--clip-home",
        default=str(Path("~").expanduser() / "Datasets" / "AISonobuoy"),
        help="the directory containing clip WAV files",
    )
    args = parser.parse_args()

    # Load file describing the collection
    collection_path = Path(args.data_home) / args.collection_filename
    collection = lu.load_json_file(collection_path)

    # Identify the interval during which any source emitted
    src_min_start_t = min([h["start_t"] for h in collection["sources"]]) * 1000  # [ms]
    src_max_stop_t = max([h["stop_t"] for h in collection["sources"]]) * 1000  # [ms]

    # Identify the interval during which all hydrophone collected
    hyd_max_start_t = (
        max([h["start_t"] for h in collection["hydrophones"]]) * 1000
    )  # [ms]
    hyd_min_stop_t = (
        min([h["stop_t"] for h in collection["hydrophones"]]) * 1000
    )  # [ms]

    # Load file describing sampling cases
    sampling = lu.load_json_file(args.sampling_filepath)

    # Consider each source
    for source in collection["sources"]:
        if source["type"] != "file":
            raise Exception("Unexpected source type")
        gpx_path = Path(args.data_home) / source["name"]
        gpx, vld_lambda, vld_varphi, vld_h, vld_t = parse_source_gpx_file(
            gpx_path, source
        )

        # Consider each hydrophone
        for hydrophone in collection["hydrophones"]:
            if hydrophone["type"] != "file":
                raise Exception("Unexpected hydrophone type")
            wav_path = Path(args.data_home) / hydrophone["name"]
            audio = lu.get_wav_file(wav_path)

            # Export audio with no source present, if it exists
            if src_max_stop_t < hyd_min_stop_t:
                lu.export_audio_clip(
                    audio,
                    src_max_stop_t,
                    hyd_min_stop_t,
                    Path(args.clip_home) / "no-boat"
                    / f"{Path(hydrophone['name'].lower()).stem}-{src_max_stop_t}-{hyd_min_stop_t}-no-source.wav",
                )

            # Compute and plot source metrics for the current hydrophone
            (
                distance,
                heading,
                heading_dot,
                speed,
                r_s_h,
                v_s_h,
            ) = lu.compute_source_metrics(
                source, vld_t, vld_lambda, vld_varphi, vld_h, hydrophone
            )
            if args.do_plot_metrics:
                lu.plot_source_metrics(
                    source, hydrophone, heading, heading_dot, distance, speed, r_s_h
                )

            # Consider each sampling case
            for case in sampling:
                clip_home = Path(args.clip_home) / case["output_dir"]
                if not clip_home.exists():
                    clip_home.mkdir(parents=True)
                method = case["method"]
                if method["type"] == "clusters":
                    (
                        distance_clusters,
                        heading_clusters,
                        heading_dot_clusters,
                        speed_clusters,
                    ) = lu.cluster_source_metrics(
                        distance,
                        method["distance_n_clusters"],
                        heading,
                        method["heading_n_clusters"],
                        heading_dot,
                        method["heading_dot_n_clusters"],
                        speed,
                        method["speed_n_clusters"],
                    )
                    slice_source_audio_by_cluster(
                        hydrophone,
                        audio,
                        hyd_max_start_t,
                        hyd_min_stop_t,
                        vld_t,
                        r_s_h,
                        distance_clusters,
                        heading_clusters,
                        heading_dot_clusters,
                        speed_clusters,
                        case["delta_t_max"],
                        case["n_clips_max"],
                        clip_home,
                        do_plot=args.do_plot_clips,
                    )
                elif method["type"] == "conditionals":
                    slice_source_audio_by_condition(
                        hydrophone,
                        audio,
                        hyd_max_start_t,
                        hyd_min_stop_t,
                        vld_t,
                        r_s_h,
                        distance,
                        method["distance_limits"],
                        heading,
                        method["heading_limits"],
                        heading_dot,
                        method["heading_dot_limits"],
                        speed,
                        method["speed_limits"],
                        case["delta_t_max"],
                        case["n_clips_max"],
                        clip_home,
                        do_plot=args.do_plot_clips,
                    )


if __name__ == "__main__":
    main()
