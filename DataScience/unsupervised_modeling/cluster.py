# system
from ast import Mod
import sys
import subprocess

# file manipulation
import os
import random

# data manipulaiton
import pandas as pd
import numpy as np

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

    cp.random.seed(SEED)
except ModuleNotFoundError:
    print(
        "If you have an NVIDIA GPU, please install cuML from https://rapids.ai/start.html#get-rapids to leverage GPU acceleration"
    )
    from sklearn.cluster import KMeans
    from umap import UMAP

# file constants
TUG_DIRNAME = "tugboat"
NOISE_DIRNAME = "no_tugboat"

# label mapping
CLASSES = {1: "Tugboat", 0: "Not Tugboat"}

# modeling constants
N_NEIGHBORS = 3
N_CLUSTERS = 2

# plotting housekeeping
sns.set_theme()

iqt_palette = [
    "#80c342",
    "#181245",
    "#f9d308",
    "#0072bc",
    "#f05343",
    "#000000",
    "#ffffff",
]
sns.set_palette(palette=iqt_palette)

# data loading by class
def load_data(file_path, tug_dirname=TUG_DIRNAME, noise_dirname=NOISE_DIRNAME):
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

    # make sure all features are of the correct shape
    assert len(set([x.shape for x in feature_tug_data])) == 1
    assert len(set([x.shape for x in feature_noise_data])) == 1

    # loaded data
    ttl_data = np.array([*feature_noise_data, *feature_tug_data])
    ttl_labels = [0] * len(feature_noise_data) + [1] * len(feature_tug_data)

    return ttl_data, ttl_labels


def model(ttl_data, n_clusters=N_CLUSTERS, seed=SEED):
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
    reducer = UMAP(n_neighbors=N_NEIGHBORS, random_state=seed)

    # result of dimensionality reduciton to plot
    reduction_results = reducer.fit_transform(ttl_data)

    # clustering algorithm
    kmeans = KMeans(n_clusters=n_clusters, random_state=seed)

    # result of clustering
    clusters = kmeans.fit_predict(ttl_data)

    # make sure that mapping is consistent
    assert len(clusters) == len(reduction_results)

    return clusters, reduction_results


def plot_two_dim_clustering(
    reduction_results,
    ttl_labels,
    clusters,
    in_file_path,
    classes_dict=CLASSES,
    n_clusters=N_CLUSTERS,
):
    """Plots a 2D side-by-side plot with ground truth and predicted labels from clustering + UMAP with Seaborn.
    
    Args:
        reduction_results (list): list of dimensionality reduced tuple x,y pairs 
        ttl_labels (list): list of class labels associated with ground truth data 
        clusters (list): list of clustering predicted labels 
        in_file_path (str): feature data directory file path
        classes_dict (dict, optional): mapping of integer values to their human readable classnames. Defaults to CLASSES.
        n_clusters (int, optional): number of clusterers from k-Means to shift color palette. Defaults to N_CLUSTERS.
    """    
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
            "pred": clusters.tolist(),
        }
    )

    # set figure size, title
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
    plt.savefig(in_file_path.split('/')[-1] + '_' + str(n_clusters) + '_' + "UMAP.png", dpi=100)


if __name__ == "__main__":
    # file constants
    # TODO: make this argparse
    ROOT = "./"
    AE_ROOT = os.path.join(ROOT, "amplitude_envelope")
    RMSE_ROOT = os.path.join(ROOT, "rmse")
    ZCR_ROOT = os.path.join(ROOT, "zcr")


    ttl_data, ttl_labels = load_data(AE_ROOT)
    clusters, reduction_results = model(ttl_data)
    plot_two_dim_clustering(
        reduction_results,
        ttl_labels,
        clusters,
        AE_ROOT,
        classes_dict=CLASSES,
        n_clusters=N_CLUSTERS,
    )
