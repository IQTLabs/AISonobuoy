import os
import torch
from torch.utils.data import Dataset

RESNET_INPUT_SHAPE = (3, 224, 224)
DATA_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset/train"
CLASS_DIRS_NAMES = "tugboat no_tugboat"


class BoatDataset(Dataset):
    def __init__(self, data_dir=DATA_ROOT, class_dir_names=CLASS_DIRS_NAMES):
        self.data_dir = data_dir
        self.classes = class_dir_names.split(' ')
        self.class_files = []
        self.files_ls = []

        for class_ in self.classes:
            self.class_files.append(
                [
                    os.path.join(data_dir, class_, x)
                    for x in os.listdir(os.path.join(data_dir, class_))
                ]
            )
            self.files_ls += [
                os.path.join(data_dir, class_, x)
                for x in os.listdir(os.path.join(data_dir, class_))
            ]

        self.class_dict = {}

    def __len__(self):
        return len(self.files_ls)

    def __getitem__(self, idx):
        curr_file = self.files_ls[idx]

        input_feature = torch.load(curr_file)
        input_feature = torch.reshape(input_feature, RESNET_INPUT_SHAPE)
        label_tensor = torch.zeros([len(CLASS_DIRS_NAMES)]).type(torch.float32)
        for i, val in enumerate(self.class_files):
            if self.class_dict:
                if i not in self.class_dict.keys():
                    self.class_dict[i] = self.classes[i]
            else:
                self.class_dict[i] = self.classes[i]
            if curr_file in val:
                label_tensor[i] = 1
                break

        return input_feature.type(torch.float32), label_tensor

if __name__ == "__main__":
    ### Tests/Debugging
    # TODO: move this into a seperate files & use pytest
    from torch.utils.data import DataLoader

    # constants
    TUGBOAT_DATA_DIR = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset/train"
    TUGBOAT_DS_CLASSES = ["tugboat", "no_tugboat"]
    TUGBOAT_FILEPATH = os.path.join(TUGBOAT_DATA_DIR, TUGBOAT_DS_CLASSES[0])
    NO_TUGBOAT_FILEPATH = os.path.join(TUGBOAT_DATA_DIR, TUGBOAT_DS_CLASSES[1])
    SAMPLING_RATE = 16000

    # instantiate class
    tugboat_ds = BoatDataset(
        data_dir=TUGBOAT_DATA_DIR,
        class_dir_names=TUGBOAT_DS_CLASSES,
    )

    # __len__() test[s]
    print("NUM TRAINING TARGETS:", len(tugboat_ds))
    assert len(tugboat_ds) == len(os.listdir(TUGBOAT_FILEPATH)) + len(
        os.listdir(NO_TUGBOAT_FILEPATH)
    )

    # __getitem__() test[s]
    dummy_dataloader = DataLoader(tugboat_ds, batch_size=1)
    X, y = next(iter(dummy_dataloader))
    assert X.squeeze(0).shape == RESNET_INPUT_SHAPE
