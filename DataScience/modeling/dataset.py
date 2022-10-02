import os
import sys
import torch
import logging
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from torch.utils.data import Dataset
import torchvision.transforms as T

import torchaudio
import librosa

RESNET_INPUT_SHAPE = (3, 224, 224)
DATA_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_final_dataset/train"
CLASS_DIRS_NAMES = ["tugboat", "no_tugboat"]


class BoatDataset(Dataset):
    def __init__(self, data_dir=DATA_ROOT, class_dir_names=CLASS_DIRS_NAMES):
        self.data_dir = data_dir
        self.classes = class_dir_names
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
        label_tensor = torch.zeros([2]).type(torch.float32)
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

    ### MAIN DATA MAINPULATION METHODS

    def _data_shape_normalization(self, signal, curr_sampling_rate):
        signal = self._resample(signal, curr_sampling_rate)
        signal = self._mix_down(signal)
        # signal = self._cut_down(signal)
        signal = self._right_pad(signal)
        return signal

    # TODO: implement value normalization (not just shape)

    ### HELPER DATA MAINPULATION METHODS

    def _resample(self, signal, curr_sampling_rate):
        if curr_sampling_rate != self.sampling_rate:
            resampler = torchaudio.transforms.Resample(
                curr_sampling_rate, self.sampling_rate
            )
            signal = resampler(signal)
        return signal

    def _mix_down(self, signal):
        if signal.shape[0] > 1:
            signal = torch.mean(signal, dim=0, keepdim=True)
        return signal

    def _cut_down(self, signal):
        if signal.shape[1] > self.num_samples:
            signal = signal[:, : self.num_samples]
        return signal

    def _right_pad(self, signal):
        if signal.shape[1] < self.num_samples:
            signal = torch.nn.functional.pad(
                signal, (0, self.num_samples - signal.shape[1])
            )
        return signal

    ### DATA VISUALIZATION METHODS

    def plot_spectrogram(
        self,
        specgram,
        title=None,
        ylabel="freq_bin",
        out_filename="test_spectrogram_new.png",
    ):
        fig, axs = plt.subplots(1, 1)
        axs.set_title(title or "Spectrogram (db)")
        axs.set_ylabel(ylabel)
        axs.set_xlabel("frame")
        im = axs.imshow(librosa.power_to_db(specgram), origin="lower", aspect="auto")
        fig.colorbar(im, ax=axs)
        plt.savefig(out_filename)


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
