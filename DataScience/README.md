The DataScience directory contains Python modules and Jupyter
Notebooks for creating labeled audio files from simultaneious audio
recordings and GPS or AIS data collections.

The GpxAudioLabeler module provides methods and a command-line
interface for the processing of the audio and GPS data collected in a
controlled environment with specified audio sources. The
AisAudioLabeler module provides methods and a command-line interface
for the processing of the audio and AIS data collected by
pibuoy-v2. The LabelerUtilites module provides methods for coordinate
transformations, clustering, and plotting, and the S3Utilities.py
module provides simplified and documented methods for interacting with
AWS S3.

== GpxAudioLabeler ==

The GpxAudioLabeler provide methods and a command-line interface for:

* Parsing a GPX file produced with a specified structure

* Exporting audio clips by heading, heading first derivative,
  distance, and speed clusters or limits

* Plot source track and label the intersection of the heading, heading
  first derivative, distance, and speed groups

Usage: GpxAudioLabeler.py [-h] [-D DATA_HOME] [-c COLLECTION_FILENAME] [-s SAMPLING_FILEPATH] [-C CLIP_HOME]
                          [-p] [-P]

Optional arguments:
  -h, --help            Show this help message and exit
  -D DATA_HOME, --data-home DATA_HOME
                        The directory containing all GPX, WAV, and JSON files
  -c COLLECTION_FILENAME, --collection-filename COLLECTION_FILENAME
                        The path of the collection JSON file to load
  -s SAMPLING_FILEPATH, --sampling-filepath SAMPLING_FILEPATH
                        The path of the sampling JSON file to process
  -C CLIP_HOME, --clip-home CLIP_HOME
                        The directory containing clip WAV files
  -p, --do-plot-clips   Do plot track with identified clips
  -P, --do-plot-metrics
                        Do plot track with computed metrics

=== Collection JSON ==

The collection JSON contains information in the following format to
describe the sources and hydrophones used during the collection.

Start and stop times are in seconds from the beginning of the
collection. Geodetic latitude, and longitude are in degrees. Elevation
is in meters.

Format:
{
    "sources": [
        {
            "type": "file" | "bucket"
            "name": "track.gpx",
            "start_t": 0,
            "stop_t": 8000.0
        }
    ],
    "hydrophones": [
        {
            "name": "unit.wav",
            "lat": 0.0,
            "lon": 0.0,
            "ele": 0.0,
            "start_t": 1000,
            "stop_t": 9000
        }
    ]
}

=== Sample JSON ===

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

Where:

* delta_t_max specifies the maximum time delta between positions in
  seconds used to define a contiguous audio sample

* n_clips_max specifies the maximum number of clips exported in each
  segment

== AisAudioLabeler ==

The AisAudioLabeler module provides methods and a command-line
interface for:

* Downloading, validating, and decompressing all objects, optionally
  identified by their prefix, in an AWS S3 bucket to a local path

* Loading all AIS files

* Probing all audio files using ffprobe

* Augmenting AIS data with distance from the hydrophone, speed, and
  ship counts when underway, or not underway

* Exporting audio clips from AIS intervals during which a specified
  maximum number of ships at a specified maximum distance are
  reporting their status as underway, and labeling the audio clip
  using the attributes of the ship closest to the hydrophone

* Plotting ship status and hydrophone recording intervals

* Plotting histogram of distance for times at which at most a
  specified maximum number of ships are reporting their status as
  underway

Usage: AisAudioLabeler.py [-h] [-D DATA_HOME] [-c COLLECTION_FILENAME] [-s SAMPLING_FILEPATH] [-C CLIP_HOME]
                          [-d] [--force-download] [--force-ais-parquet] [--force-hmd-parquet] [--force-shp-json]
                          [--export-clips] [--plot-intervals] [--plot-histogram]

Optional arguments:
  -h, --help            Show this help message and exit
  -D DATA_HOME, --data-home DATA_HOME
                        The directory containing all downloaded AIS files
  -c COLLECTION_FILENAME, --collection-filename COLLECTION_FILENAME
                        The path of the collection JSON file to load
  -d, --decompress      Decompress downloaded files
  --force-download      Force file download
  --force-ais-parquet   Force AIS parquet creation
  --force-hmd-parquet   Force hydrophone metadata parquet creation
  --force-shp-json      Force SHP JSON creation
  -s SAMPLING_FILEPATH, --sampling-filepath SAMPLING_FILEPATH
                        The path of the sampling JSON file to process
  --plot-intervals      Do plot ship status and hydrophone recording intervals
  --plot-histogram      Do plot ship distance from hydrophone histogram
  --export-clips        Do export audio clips
  -C CLIP_HOME, --clip-home CLIP_HOME
                        The directory containing clip WAV files

=== Collection JSON ==

The collection JSON contains information in the following format to
describe the sources and hydrophones used during the collection.

Geodetic latitude, and longitude are in degrees. Elevation is in
meters.

Format:
{
    "sources": [
        {
            "type": "bucket",
            "name": "aisonobuoy-pibuoy-v2",
            "prefix": "compressed"
        }
    ],
    "hydrophones": [
        {
            "type": "bucket",
            "name": "aisonobuoy-pibuoy-v2",
            "prefix": "compressed",
            "lat": 0.0,
            "lon": 0.0,
            "ele": 0.0
        }
    ]
}

=== Sample JSON ===

The sample JSON document contains entries in the following format
which describe the method, and its parameters, used in creating
labeled samples from the collection.

The distance is in meters.

Format:
[
    {
        "name": "default",
        "max_n_ships": 3,
        "max_distance": 500.0,
        "output_dir": "no-more-than-three-or-500-m-then-min-distance"
    }
]

Where:

* max_n_ships specifies the maximum number of ships underway
  simultaneously

* max_distance specifies the maximum distance of ships underway
  simultaneously from the hydrophone

== LabelerUtilites ==

The LabelerUtilites module provides methods for:

* Computing the geocentric position given geodetic longitude and
  latitude, and elevation

* Computing geocentric east, north, and zenith unit vectors at a given
  geodetic longitude and latitude, and the corresponding orthogonal
  transformation matrix from geocentric to topocentric coordinates

* Computing the topocentric position and velocity of the source
  relative to the hydrophone, and corresponding heading, heading first
  derivative, distance, and speed

* Computing clusters of distance, heading, heading first derivative,
  and speed

* Plotting source track, and histograms of source distance, heading,
  heading first derivative, and speed






