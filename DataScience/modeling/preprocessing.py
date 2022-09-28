import os
from xml.dom import NotFoundErr
import torchaudio
import librosa
import torch
import random
import numpy as np
import matplotlib.pyplot as plt
import torch.nn as nn

SAMPLING_RATE = 16000
FRAME_LENGTH = 1024 * 3 // 7
HOP_LENGTH = FRAME_LENGTH // 2
WINDOW_LENGTH = FRAME_LENGTH
NUM_MELS = 64
NUM_SAMPLES = 22500

TARGET_WINDOW_SIZE_SECONDS = 3

ROOT = "/home/achadda/tugboat_dataset"
CLASS_DIR_NAMES = ["tugboat", "no_tugboat"]
OUT_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_dataset_compressed_specgrams"

SEED = 1
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True


class PreProcess:
    def __init__(
        self,
        data_dir=ROOT,
        class_dir_names=CLASS_DIR_NAMES,
        sampling_rate=SAMPLING_RATE,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH,
        window_length=WINDOW_LENGTH,
        num_mels=NUM_MELS,
        num_samples=NUM_SAMPLES,
        transformation=torchaudio.transforms.Spectrogram(
            n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH, power=2
        ),
    ):
        self.data_dir = data_dir
        self.class_names = class_dir_names
        self.classes = class_dir_names
        self.class_files = []
        self.files_ls = []
        self.sampling_rate = sampling_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.window_length = window_length
        self.num_mels = num_mels
        self.num_samples = num_samples
        self.transformation = transformation
        self.save_ls = []
        self.ctr = 0

        for class_ in self.classes:
            self.class_files.append(
                set(
                    os.path.join(data_dir, class_, x)
                    for x in os.listdir(os.path.join(data_dir, class_))
                )
            )
            self.files_ls += [
                os.path.join(data_dir, class_, x)
                for x in os.listdir(os.path.join(data_dir, class_))
            ]

        self.class_dict = {}
        self.class_counter = {}

    def process(self, idx):
        input_feature = None # the pytorch hash function hashes objects not data 
        curr_file = self.files_ls[idx]

        data, curr_sampling_rate = torchaudio.load(curr_file)
        bucket_size = curr_sampling_rate * TARGET_WINDOW_SIZE_SECONDS
        if len(data[0]) > bucket_size:
            prev = 0
            for idx in range(bucket_size, len(data[0]), bucket_size):
                snippet = data[0][prev:idx]
                prev = idx
                assert len(snippet) / curr_sampling_rate == TARGET_WINDOW_SIZE_SECONDS

                input_feature = self._create_feature_representation(snippet)
                input_feature = nn.functional.pad(
                    input_feature, (2, 2, 2, 2), "constant", 0
                )
                for i, val in enumerate(self.class_files):
                    if self.class_dict:
                        if i not in self.class_dict.keys():
                            self.class_dict[i] = self.classes[i]
                    else:
                        self.class_dict[i] = self.classes[i]
                    if curr_file in val:
                        label = i
                        break
                self.save_ls.append(input_feature)
                self._save_tensors(label, input_feature)

    ### MAIN DATA MAINPULATION METHODS

    def _create_feature_representation(self, signal):
        input_feature = self.transformation(signal)
        return input_feature

    def _save_tensors(self, label, input_feature):
        # save_path = os.path.join(
        #     OUT_ROOT, self.class_dict[label], str(self.ctr) + ".pt"
        # )

        save_path = os.path.join(OUT_ROOT, self.class_dict[label], hex(hash(input_feature)) + '.pt')

        input_feature = torch.flatten(input_feature)
        torch.save(input_feature, save_path)
        self.ctr += 1

    ### DATA VISUALIZATION METHODS

    def plot_spectrogram(
        self,
        specgram,
        title=None,
        ylabel="freq_bin",
        out_filename="test_spectrogram.png",
    ):
        fig, axs = plt.subplots(1, 1)
        axs.set_title(title or "Spectrogram (db)")
        axs.set_ylabel(ylabel)
        axs.set_xlabel("frame")
        im = axs.imshow(librosa.power_to_db(specgram), origin="lower", aspect="auto")
        fig.colorbar(im, ax=axs)
        plt.savefig(out_filename)


if __name__ == "__main__":
    # TODO: move to seperate file w/ pytest & add more tests
    preprocesser = PreProcess(
        data_dir="/home/achadda/tugboat_dataset",
        class_dir_names=["tugboat", "no_tugboat"],
    )

    for idx in range(len(preprocesser.files_ls)):
        preprocesser.process(idx)

    assert len(set(preprocesser.save_ls)) == len(preprocesser.save_ls)
