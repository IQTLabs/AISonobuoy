from argparse import ArgumentParser
from datetime import datetime
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


def get_source_wav_file(inp_path):
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
    audio = AudioSegment.from_wav(inp_path)
    return audio


def compute_source_metrics(gpx):
    """Compute the topocentric position and velocity of the source
    relative to the origin, and corresponding heading, heading first
    derivative, and speed.

    Parameters
    ----------
    gpx : dict
        Track, track segments, and track points

    Returns
    -------
    vld_t : numpy.ndarray
        Time from start of track [s]
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_dot : numpy.ndarray
        Source heading first derivative
    speed : numpy.ndarray
        Source speed [m/s]
    r_s_o : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]
    v_s_o : numpy.ndarray
        Source topocentric (east, north, zenith) velocity [m/s]

    See:
    Montenbruck O., Gill E.; Satellite Orbits; Springer, Berlin (2001); pp. 37 and 38.
    """
    # Assign longitude, latitude, elevation, and time from start of
    # track
    # TODO: Check single track and track segment assumption
    _lambda = np.array(gpx["trks"][0]["trksegs"][0]["lon"])  # geodetic longitude [rad]
    _varphi = np.array(gpx["trks"][0]["trksegs"][0]["lat"])  # geodetic latitude [rad]
    _h = np.array(gpx["trks"][0]["trksegs"][0]["ele"])  # elevation [m]
    _t = np.array(gpx["trks"][0]["trksegs"][0]["time"])  # time from start of track [s]

    # Ignore points at which the elevation was not recorded
    vld_idx = _h != -R_OPLUS
    vld_lambda = _lambda[vld_idx]
    vld_varphi = _varphi[vld_idx]
    vld_h = _h[vld_idx]
    vld_t = _t[vld_idx]

    # Compute geocentric east, north, and zenith unit vectors at an
    # origin corresponding to the mean longitude and latitude, and the
    # corresponding orthogonal transformation matrix from geocentric
    # to topocentric coordinates
    mean_lambda = np.mean(vld_lambda)
    mean_varphi = np.mean(vld_varphi)
    mean_h = np.mean(vld_h)
    e_E = np.array([-math.sin(mean_lambda), math.cos(mean_lambda), 0])
    e_N = np.array(
        [
            -math.sin(mean_varphi) * math.cos(mean_lambda),
            -math.sin(mean_varphi) * math.sin(mean_lambda),
            math.cos(mean_varphi),
        ]
    )
    e_Z = np.array(
        [
            math.cos(mean_varphi) * math.cos(mean_lambda),
            math.cos(mean_varphi) * math.sin(mean_lambda),
            math.sin(mean_varphi),
        ]
    )
    E = np.row_stack((e_E, e_N, e_Z))

    # Compute the geocentric position of the origin
    f = 1 / F_INV
    N_o = R_OPLUS / math.sqrt(1 - f * (2 - f) * math.sin(mean_varphi) ** 2)
    R_o = np.array(
        [
            (N_o + mean_h) * math.cos(mean_varphi) * math.cos(mean_lambda),
            (N_o + mean_h) * math.cos(mean_varphi) * math.sin(mean_lambda),
            ((1 - f) ** 2 * N_o + mean_h) * math.sin(mean_varphi),
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
    # origin
    R_s_o = R_s - np.atleast_2d(R_o).reshape(3, 1)

    # Compute the topocentric position and velocity of the source
    # relative to the origin, and corresponding heading, heading first
    # derivative, and speed
    # TODO: Use instantaneous orthogonal transformation matrix?
    r_s_o = np.matmul(E, R_s_o)
    v_s_o = np.gradient(r_s_o, vld_t, axis=1)
    heading = 90 - np.degrees(np.arctan2(v_s_o[1, :], v_s_o[0, :]))
    heading_dot = (
        pd.DataFrame(np.gradient(heading, vld_t)).ewm(span=3).mean().to_numpy()
    ).flatten()
    speed = np.sqrt(np.sum(np.square(v_s_o), axis=0))
    return vld_t, heading, heading_dot, speed, r_s_o, v_s_o


def plot_source_metrics(heading, heading_dot, speed, r_s_o):
    """Plot source track, and histograms of source heading and speed.

    Parameters
    ----------
    heading : numpy.ndarray
        Source heading, zero at north, clockwise positive
    heading_dot : numpy.ndarray
        Source heading first derivative
    speed : numpy.ndarray
        Source speed [m/s]
    r_s_o : numpy.ndarray
        Source topocentric (east, north, zenith) position [m]

    Returns
    -------
    None
    """
    fig, axs = plt.subplots()
    axs.plot(r_s_o[0, :], r_s_o[1, :])
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
    heading_kmeans = KMeans(n_clusters=heading_n_clusters, random_state=0).fit(
        90 - heading.reshape(-1, 1)
    )
    speed_kmeans = KMeans(n_clusters=speed_n_clusters, random_state=0).fit(
        speed.reshape(-1, 1)
    )
    return heading_kmeans, speed_kmeans


def slice_source_audio_by_cluster(
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
    # Assign cluster centers and ensure heading clusters pair
    heading_centers = heading_kmeans.cluster_centers_
    heading_n_clusters = len(heading_centers)

    if np.sum(heading_centers > 0) != np.sum(heading_centers < 0):
        raise Exception("Number of positive and negative heading centers must be equal")

    speed_centers = speed_kmeans.cluster_centers_
    speed_n_clusters = len(speed_centers)

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
                        n_clips += 1
                        start_t = int(dub_t_set[0] * 1000)
                        stop_t = int(dub_t_set[-1] * 1000)
                        clip = audio[start_t:stop_t]
                        wav_filename = "clip-{:d}-{:d}-{:+.1f}{:+.1f}"
                        if isgreater:
                            wav_filename += "-greater"
                        else:
                            wav_filename += "-lesser"
                        wav_filename += "{:+.1f}.wav"
                        clip.export(
                            clip_home
                            / wav_filename.format(
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
                    title = "headings = {:.1f}, {:.1f} deg"
                    if isgreater:
                        title += ", heading_dot > 1"
                    else:
                        title += ", heading_dot < 1"
                    title += ", speed = {:.1f} m/s"
                    axs.set_title(
                        title.format(
                            heading_centers[pos_lbl_idx][0],
                            heading_centers[neg_lbl_idx][0],
                            speed_centers[spd_lbl_idx][0],
                        )
                    )
                    axs.set_xlabel("east [m]")
                    axs.set_ylabel("north [m]")
                    plt.show()


"""Demonstrate GpxLabeler.
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
        "-g",
        "--gpx-filename",
        default="suuntoapp-Motorsports-2022-02-22T18-09-01Z-track.gpx",
        help="the GPX filename to parse",
    )
    parser.add_argument(
        "-w",
        "--wav-filename",
        default="Unit-01.WAV",
        help="the WAV filename to open",
    )
    parser.add_argument(
        "-d",
        "--heading-n-clusters",
        type=int,
        default=10,
        help="the number of heading cluster means",
    )
    parser.add_argument(
        "-s",
        "--speed-n-clusters",
        type=int,
        default=4,
        help="the maximum time delta between positions used to define a contiguous audio sample [s]",
    )
    parser.add_argument(
        "-t",
        "--delta-t-max",
        type=float,
        default=4.0,
        help="the maximum time delta between positions used to define a contiguous audio sample [s]",
    )
    parser.add_argument(
        "-t",
        "--delta-t-max",
        type=float,
        default=4.0,
        help="the maximum time delta between positions used to define a contiguous audio sample [s]",
    )
    parser.add_argument(
        "-n",
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

    gpx_path = Path(args.data_home) / args.gpx_filename
    wav_path = Path(args.data_home) / args.wav_filename

    gpx = parse_source_gpx_file(gpx_path)
    audio = get_source_wav_file(wav_path)

    vld_t, heading, heading_dot, speed, r_s_o, v_s_o = compute_source_metrics(gpx)

    plot_source_metrics(heading, heading_dot, speed, r_s_o)

    heading_kmeans, speed_kmeans = kmeans_cluster_source_metrics(
        heading,
        args.heading_n_clusters,
        speed,
        args.speed_n_clusters,
    )

    slice_source_audio_by_cluster(
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
