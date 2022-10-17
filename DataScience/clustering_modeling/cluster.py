# file manipulation
import os
import random

# data manipulaiton
import ast
import pandas as pd
import numpy as np
from statistics import mean, median

# plotting
import matplotlib.pyplot as plt
import seaborn as sns

# set seed
SEED = 1
random.seed(SEED)
np.random.seed(SEED)

# modeling
try:
    from cuml import KMeans
    from cuml.manifold import UMAP
    import cupy as cp
    from cuml.metrics import trustworthiness

    cp.random.seed(SEED)
except ModuleNotFoundError:
    print(
        "If you have an NVIDIA GPU, please install cuML from https://rapids.ai/start.html#get-rapids to leverage GPU acceleration"
    )
    from sklearn.cluster import KMeans
    from umap import UMAP
    from sklearn.manifold import trustworthiness

# file constants
TUG_DIRNAME = "tugboat"
NOISE_DIRNAME = "no_tugboat"

# label mapping
CLASSES = "{1: 'Tugboat', 0: 'Not Tugboat'}"

# modeling constants
N_NEIGHBORS = 3
N_CLUSTERS = 2

OUT_DIR = "./"

# plotting housekeeping
sns.set_theme(style="white")

iqt_palette = [
    "#80c342",
    "#181245",
    "#f9d308",
    "#0072bc",
    "#f05343",
    "#65cbe7",
    "#6657d3",
    "#5f6475",
    "#951306",
    "#3e641e",
]
sns.set_palette(palette=iqt_palette)

# data loading by class
def load_data(
    file_path, tug_dirname=TUG_DIRNAME, noise_dirname=NOISE_DIRNAME, out_dir=OUT_DIR
):
    """Load the feature data + labels into memory

    Args:
        file_path (str): the file path of the feature directory of interest
        tug_dirname (str, optional): the name a class sub-directory. Defaults to TUG_DIRNAME.
        noise_dirname (str, optional): the name another class sub-directory. Defaults to NOISE_DIRNAME.

    Returns:
        list: the feature data points on which to make predicitons + dimensionally reduce
        list: list of class labels associated with ground truth data
    """
    feature_tug_data = [
        np.load(os.path.join(file_path, tug_dirname, x))
        for x in os.listdir(os.path.join(file_path, tug_dirname))
    ]

    feature_noise_data = random.sample(
        [
            np.load(os.path.join(file_path, noise_dirname, x))
            for x in os.listdir(os.path.join(file_path, noise_dirname))
        ],
        len(feature_tug_data),
    )

    plot_feature_distributions(feature_tug_data, feature_noise_data, file_path, out_dir)

    # loaded data
    ttl_data = np.array([*feature_noise_data, *feature_tug_data])
    ttl_labels = [0] * len(feature_noise_data) + [1] * len(feature_tug_data)

    return ttl_data, ttl_labels


def plot_feature_distributions(
    feature_tug_data, feature_noise_data, in_file_path, out_dir
):
    """creates and saves a distribution plot of various summary metrics of a feature

    Args:
        feature_tug_data (list): list of numpy arrays of the generated feature for the tug data
        feature_noise_data (list): list of numpy arrays of the generated feature for the noise data
        in_file_path (str): filepath of input data
        out_dir (str): filepath to save figure to
    """
    # label of current feature
    plt.figure(figsize=(9, 6.5))  # 100px per in
    curr_feature_label = " ".join(in_file_path.split("/")[-1].split("_")).upper()

    # create a dataframe of summary metrics
    values_df = pd.DataFrame.from_dict(
        {
            "tug_max": [max(x) for x in feature_tug_data],
            "tug_min": [min(x) for x in feature_tug_data],
            "tug_mean": [mean(x) for x in feature_tug_data],
            "tug_median": [median(x) for x in feature_tug_data],
            "noise_max": [max(x) for x in feature_noise_data],
            "noise_min": [min(x) for x in feature_noise_data],
            "noise_mean": [mean(x) for x in feature_noise_data],
            "noise_median": [median(x) for x in feature_noise_data],
        }
    )

    # plot smoothed distributions of summary metrics
    sns.displot(data=values_df, kind="kde", height=8)

    # chart formatting
    plt.title(f"Distribution of Summary Metrics — {curr_feature_label}")
    plt.xlabel(curr_feature_label)
    plt.tick_params(bottom=False, left=False)
    plt.yticks(color="w")
    plt.xticks(color="w")
    # save figure
    plt.savefig(
        os.path.join(
            out_dir,
            in_file_path.split("/")[-1] + "_summary_metrics_distplot.png",
        ),
        dpi=100,
        bbox_inches="tight",
    )

    plt.close()


def model(ttl_data, n_clusters=N_CLUSTERS, n_neighbors=N_NEIGHBORS, seed=SEED):
    """loads the UMAP and clustering algorithms and generates predictions + dimensionality reduction on data

    Args:
        ttl_data (list): the feature data points on which to make predicitons + dimensionally reduce
        n_clusters (int, optional): number of clusters for k-Means clustering. Defaults to N_CLUSTERS.
        seed (int, optional): random seed to set for reproducibilty. Defaults to SEED.

    Returns:
        list: list of clustering predicted labels
        list: list of dimensionality reduced tuple x,y pairs
    """
    # dimensionality reduction algorithm for plotting
    reducer = UMAP(n_neighbors=n_neighbors, random_state=seed)

    # result of dimensionality reduciton to plot
    reduction_results = reducer.fit_transform(ttl_data)

    # trustworthiness score
    trust = trustworthiness(ttl_data, reduction_results, n_neighbors=n_neighbors)

    # clustering algorithm
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed)

    # result of clustering
    clusters = kmeans.fit_predict(ttl_data)

    return clusters, reduction_results, trust


def plot_two_dim_clustering(
    reduction_results,
    ttl_labels,
    clusters,
    in_file_path,
    out_dir=OUT_DIR,
    classes_dict=CLASSES,
    n_clusters=N_CLUSTERS,
    n_neighbors=N_NEIGHBORS,
):
    """Plots a 2D side-by-side plot with ground truth and predicted labels from clustering + UMAP with Seaborn.

    Args:
        reduction_results (list): list of dimensionality reduced tuple x,y pairs
        ttl_labels (list): list of class labels associated with ground truth data
        clusters (list): list of clustering predicted labels
        in_file_path (str): feature data directory file path
        out_dir (str): path to directory to save plots to
        classes_dict (dict, optional): mapping of integer values to their human readable classnames. Defaults to CLASSES.
        n_clusters (int, optional): number of clusterers from k-Means to shift color palette. Defaults to N_CLUSTERS.

    """
    # create distribution plot of preds v. ground truth and save
    plot_label_distributions(ttl_labels, clusters, in_file_path, out_dir)

    # split x,y for plotting
    x_arr = []
    y_arr = []
    for pt in reduction_results.tolist():
        x_arr.append(pt[0])
        y_arr.append(pt[-1])

    # create dataframe to plot
    pred_gt_df = pd.DataFrame.from_dict(
        {
            "x": x_arr,
            "y": y_arr,
            "gt": [*map(classes_dict.get, ttl_labels, ttl_labels)],
            "pred": clusters,
        }
    )

    # set figure size, title, and palette
    sns.set_palette(palette=iqt_palette)
    fig, axes = plt.subplots(1, 2)
    fig.set_size_inches(12, 10)  # 100px per in
    fig.suptitle(
        f"k-Means Clustering of Tugboat/No Tugboat Dataset — {' '.join(in_file_path.split('/')[-1].split('_')).upper()}"
    )

    # create first subplot for ground truth labels
    plt_one = sns.scatterplot(ax=axes[0], data=pred_gt_df, x="x", y="y", hue="gt", s=3)
    plt_one.set_title("Ground Truth")
    plt_one.tick_params(bottom=False, left=False)
    plt_one.set(xticklabels=[])
    plt_one.set(xlabel=None)
    plt_one.set(yticklabels=[])
    plt_one.set(ylabel=None)
    plt_one.legend(
        bbox_to_anchor=(0, 0),
        loc="lower left",
        bbox_transform=fig.transFigure,
        ncol=3,
        title="Class Labels",
    )

    # create second subplot for predictions
    sns.set_palette(palette=iqt_palette[n_clusters:])
    plt_two = sns.scatterplot(
        ax=axes[1], data=pred_gt_df, x="x", y="y", hue="pred", s=3
    )
    plt_two.set_title("Predictions")
    plt_two.set(xticklabels=[])
    plt_two.set(xlabel=None)
    plt_two.set(yticklabels=[])
    plt_two.set(ylabel=None)
    plt_two.legend(
        bbox_to_anchor=(1, 0),
        loc="lower right",
        bbox_transform=fig.transFigure,
        ncol=3,
        title="Predicted Labels",
    )

    # save figure
    plt.savefig(
        os.path.join(
            out_dir,
            in_file_path.split("/")[-1]
            + "_clusters_"
            + str(n_clusters)
            + "_neighbors_"
            + str(n_neighbors)
            + "_"
            + "UMAP.png",
        ),
        dpi=100,
        bbox_inches="tight",
    )
    plt.close()


def plot_label_distributions(ttl_labels, clusters, in_file_path, out_dir):
    """create distribution plot of preds v. ground truth and save

    Args:
        ttl_labels (list): list of class labels associated with ground truth data
        clusters (list): list of clustering predicted labels
        in_file_path (str): feature data directory file path
        out_dir (str): path to directory to save plots to
    """
    # label of current feature
    curr_feature_label = " ".join(in_file_path.split("/")[-1].split("_")).upper()

    # create a dataframe of summary metrics
    label_df = pd.DataFrame.from_dict({"gt": ttl_labels, "preds": clusters})

    # plot distributions of labels v. groundtruth
    plt.figure(figsize=(4, 6.5))
    sns.histplot(data=label_df, element="step")
    plt.xticks([0, 1])

    # chart formatting
    plt.title(
        f"Distribution of Predicted Labels v. Ground Truth Labels {curr_feature_label}"
    )
    plt.xlabel(curr_feature_label)

    # save figure
    plt.savefig(
        os.path.join(
            out_dir,
            in_file_path.split("/")[-1] + "_pred_ground_truth_label_distplot.png",
        ),
        dpi=100,
        bbox_inches="tight",
    )

    plt.close()


if __name__ == "__main__":
    # file constants
    ROOT = "./"
    AE_ROOT = os.path.join(ROOT, "amplitude_envelope")
    RMSE_ROOT = os.path.join(ROOT, "rmse")
    ZCR_ROOT = os.path.join(ROOT, "zcr")
    SF_ROOT = os.path.join(ROOT, "spectral_flux")
    SB_ROOT = os.path.join(ROOT, "spectral_bandwidth")
    SC_ROOT = os.path.join(ROOT, "spectral_centroid")
    BER_ROOT = os.path.join(ROOT, "band_energy_ratio")

    DIR_LS = [AE_ROOT, RMSE_ROOT, ZCR_ROOT, SF_ROOT, SB_ROOT, SC_ROOT, BER_ROOT]

    OUT_DIR = "./out_graphs"

    NEIGHBORS_LS = [
        2,
        3,
        4,
        5,
        6,
        7,
        8,
        9,
        10,
        11,
        12,
        13,
        14,
        15,
        16,
        17,
        18,
        19,
        20,
        21,
        22,
        23,
        24,
        25,
    ]

    for curr_dir in DIR_LS:
        trustworthiness_ls = []
        cluster_ls = []
        reduction_ls = []
        print(f"Making graph for {curr_dir}")
        ttl_data, ttl_labels = load_data(curr_dir, out_dir=OUT_DIR)
        for neighbor in NEIGHBORS_LS:
            clusters, reduction_results, trust = model(
                ttl_data, n_clusters=N_CLUSTERS, n_neighbors=neighbor
            )
            trustworthiness_ls.append(trust)
            cluster_ls.append(clusters)
            reduction_ls.append(reduction_results)

        idx = np.array(trustworthiness_ls).argmax()

        plot_two_dim_clustering(
            reduction_ls[idx],
            ttl_labels,
            cluster_ls[idx],
            curr_dir,
            OUT_DIR,
            classes_dict=ast.literal_eval(CLASSES),
            n_clusters=N_CLUSTERS,
            n_neighbors=NEIGHBORS_LS[idx],
        )
