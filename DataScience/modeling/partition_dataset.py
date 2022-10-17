# file manipulation
import os
import random
import shutil

# infile constants
ROOT = "/home/achadda/sonobuoy_modeling/tugboat_dataset_compressed_specgrams/"
CLASS_DIRS = os.listdir(ROOT)

# outfile constants
DATASET_OUT_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset"
DATASET_OUT_TRAIN = os.path.join(DATASET_OUT_ROOT, "train")
DATASET_OUT_TEST = os.path.join(DATASET_OUT_ROOT, "test")
DATASET_OUT_VAL = os.path.join(DATASET_OUT_ROOT, "val")

# get classnames
class_data_dict = {
    class_: set(os.listdir(os.path.join(ROOT, class_))) for class_ in CLASS_DIRS
}

# avoid class imbalance by including equal # of targets per class
class_num_targets = len(min(class_data_dict.values(), key=len))

# ~70% train, ~20% test, ~10% val
train_num_targets = int(class_num_targets * 0.7)
test_num_targets = int(class_num_targets * 0.2)
val_num_targets = class_num_targets - train_num_targets - test_num_targets

# create out directories
os.makedirs(DATASET_OUT_ROOT, exist_ok=True)
os.makedirs(DATASET_OUT_TRAIN, exist_ok=True)
os.makedirs(DATASET_OUT_TEST, exist_ok=True)
os.makedirs(DATASET_OUT_VAL, exist_ok=True)

# for classname and target files for each class
for class_name, rem_class_targets in class_data_dict.items():
    # outfile class directory paths
    train_path = os.path.join(DATASET_OUT_TRAIN, class_name)
    test_path = os.path.join(DATASET_OUT_TEST, class_name)
    val_path = os.path.join(DATASET_OUT_VAL, class_name)

    # create outfile paths for class
    os.makedirs(train_path)
    os.makedirs(test_path)
    os.makedirs(val_path)

    # use set subtraction to make sure there are no duplicates and partition sets randomly
    train_targets = set(random.sample(rem_class_targets, train_num_targets))
    rem_class_targets -= train_targets
    test_targets = set(random.sample(rem_class_targets, test_num_targets))
    rem_class_targets -= test_targets
    val_targets = set(random.sample(rem_class_targets, val_num_targets))
    rem_class_targets -= val_targets

    # copy files in each subset into partition directories
    for file in train_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), train_path)

    for file in test_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), test_path)

    for file in val_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), val_path)
