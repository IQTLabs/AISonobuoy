# file manipulation
import os

# data manipulation
import torch
from torch.utils.data import Dataset

# outshape
RESNET_INPUT_SHAPE = (3, 224, 224)

# file constants
DATA_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset/train"
CLASS_DIRS_NAMES = "tugboat no_tugboat"


class BoatDataset(Dataset):
    """PyTorch dataset class that mirrors torchvision.datasets.DatasetFolder format

    Args:
        Dataset (torch.utils.data.Dataset): PyTorch Datatset class for training models
    """

    def __init__(self, data_dir=DATA_ROOT, class_dir_names=CLASS_DIRS_NAMES):
        """initializes class enviornment variables and loads files + labels into memory

        Args:
            data_dir (str, optional): file path to root of saved PyTorch tensor files. Defaults to DATA_ROOT.
            class_dir_names (str, optional): space delimited string of classname where each class is separated by a space. Defaults to CLASS_DIR_NAMES.
        """
        # assiging parameters
        self.data_dir = data_dir
        self.classes = class_dir_names.split(" ")
        self.class_files = []
        self.files_ls = []
        self.class_dict = {}

        # loading filenames into memory
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

    def __len__(self):
        """Required PyTorch Dataset class __len__() override that gives the length of dataset

        Returns:
            int: length of dataset
        """
        # return the length of the file list
        return len(self.files_ls)

    def __getitem__(self, idx):
        """Required PyTorch Dataset class __getitem__() override that serves up a feature-label pair

        Args:
            idx (int): index of value item value to serve up

        Returns:
            torch.Tensor: feature tensor of shape RESNET_INPUT_SHAPE
            torch.Tensor: one-hot encoded class label tensor
        """
        # get filename to render
        curr_file = self.files_ls[idx]

        # load tensor into memory
        input_feature = torch.load(curr_file)
        # torch.save() flattens tensors when saving, so they need to be reshaped to their orignial shape when loaded
        input_feature = torch.reshape(input_feature, RESNET_INPUT_SHAPE)
        # create label tensor for one-hot encoding
        label_tensor = torch.zeros([len(CLASS_DIRS_NAMES)]).type(torch.float32)
        # assign a "1" to the relevant slot in the tensor which corresponds to a class
        for i, val in enumerate(self.class_files):
            if self.class_dict:
                if i not in self.class_dict.keys():
                    self.class_dict[i] = self.classes[i]
            else:
                self.class_dict[i] = self.classes[i]
            if curr_file in val:
                label_tensor[i] = 1
                break

        # return feature (X) and label (y)
        return input_feature.type(torch.float32), label_tensor
