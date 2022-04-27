The collection JSON contains information in the following format
to describe the sources and hydrophones used during the
collection.

Start and stop times are in seconds. Latitude, and longitude are
in degrees. Elevation is in meters.

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
