import os
import random
import shutil

ROOT = "/home/achadda/sonobuoy_modeling/tugboat_dataset_compressed_specgrams/"
CLASS_DIRS = os.listdir(ROOT)

DATASET_OUT_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset"
DATASET_OUT_TRAIN = os.path.join(DATASET_OUT_ROOT, "train")
DATASET_OUT_TEST = os.path.join(DATASET_OUT_ROOT, "test")
DATASET_OUT_VAL = os.path.join(DATASET_OUT_ROOT, "val")

class_data_dict = {
    class_: set(os.listdir(os.path.join(ROOT, class_))) for class_ in CLASS_DIRS
}

# avoid class imbalance by including equal # of targets per class
class_num_targets = len(min(class_data_dict.values(), key=len))

train_num_targets = int(class_num_targets * 0.7)
test_num_targets = int(class_num_targets * 0.2)
val_num_targets = class_num_targets - train_num_targets - test_num_targets

os.makedirs(DATASET_OUT_ROOT, exist_ok=True)
os.makedirs(DATASET_OUT_TRAIN, exist_ok=True)
os.makedirs(DATASET_OUT_TEST, exist_ok=True)
os.makedirs(DATASET_OUT_VAL, exist_ok=True)

for class_name, rem_class_targets in class_data_dict.items():
    train_path = os.path.join(DATASET_OUT_TRAIN, class_name)
    test_path = os.path.join(DATASET_OUT_TEST, class_name)
    val_path = os.path.join(DATASET_OUT_VAL, class_name)

    os.makedirs(train_path)
    os.makedirs(test_path)
    os.makedirs(val_path)

    train_targets = set(random.sample(rem_class_targets, train_num_targets))
    rem_class_targets -= train_targets
    test_targets = set(random.sample(rem_class_targets, test_num_targets))
    rem_class_targets -= test_targets
    val_targets = set(random.sample(rem_class_targets, val_num_targets))
    rem_class_targets -= val_targets

    for file in train_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), train_path)

    for file in test_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), test_path)

    for file in val_targets:
        shutil.copy(os.path.join(ROOT, class_name, file), val_path)
