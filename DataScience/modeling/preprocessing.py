# file manipulation
import os

# data manipulation
import torch
import random
import numpy as np

# audio manipulation libraries
import torchaudio
import librosa

# image manipulation
import cv2
import torch.nn.functional as F

# data visualization
import matplotlib.pyplot as plt

# audio preprocessing constants
SAMPLING_RATE = 16000
FRAME_LENGTH = 1024 * 3 // 7
HOP_LENGTH = FRAME_LENGTH // 2
WINDOW_LENGTH = FRAME_LENGTH
TARGET_WINDOW_SIZE_SECONDS = 3

# file path constants
ROOT = "/home/achadda/tugboat_dataset"
CLASS_DIR_NAMES = "tugboat no_tugboat"
TENSOR_OUT_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_dataset_compressed_specgrams"
IMAGE_OUT_ROOT = "/home/achadda/sonobuoy_modeling/tugboat_dataset_image_specgrams"

# fix randomness for reproducibility
SEED = 1
random.seed(SEED)
np.random.seed(SEED)
torch.manual_seed(SEED)
torch.cuda.manual_seed(SEED)
torch.backends.cudnn.deterministic = True


def create_image_spectrogram(specgram):
    """

    Args:
        specgram (torch.tensor): PyTorch tensor sinppet corresponding to spectrogram of audio segment to convert to visual representation

    Returns:
        torch.tensor: PyTorch tensor corresponding to visual spectrogram
    """
    # create size of matplotlib plot
    sizes = np.shape(specgram)
    fig, axs = plt.subplots(1, 1)
    fig.set_size_inches(1.0 * sizes[0] / sizes[1], 1, forward=False)
    # plot spectrogram in log decible scale
    im = axs.imshow(
        librosa.power_to_db(specgram),
        origin="lower",
        aspect="auto",
        vmin=-80,
        vmax=80,
        cmap="turbo",
    )
    # convert to image and PyTorch image channel format (color channel first)
    arr = im.make_image(renderer=None, unsampled=True)[0]
    arr = np.moveaxis(arr, -1, 0)
    arr = torch.from_numpy(arr)
    arr = arr[:3, :, :]
    plt.close()
    # return torch tensor visual spectrogram
    return arr


class PreProcess:
    """class to transform raw audio files into some visual audio representation"""

    def __init__(
        self,
        data_dir=ROOT,
        class_dir_names=CLASS_DIR_NAMES,
        sampling_rate=SAMPLING_RATE,
        frame_length=FRAME_LENGTH,
        hop_length=HOP_LENGTH,
        window_length=WINDOW_LENGTH,
        transformation=torchaudio.transforms.Spectrogram(
            n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH, power=2
        ),
        feature_func=create_image_spectrogram,
    ):
        """initializes class enviornment variables and loads files + labels into memory

        Args:
            data_dir (str, optional): file path to root of (.wav) audio data files to preprocess. Defaults to ROOT.
            class_dir_names (str, optional): space delimited string of classname where each class is separated by a space. Defaults to CLASS_DIR_NAMES.
            sampling_rate (int, optional): sampling rate of audio files. Defaults to SAMPLING_RATE.
            frame_length (int, optional): frame length for spectrogram calculation. Defaults to FRAME_LENGTH.
            hop_length (int, optional): hop length for spectrogram calculation. Defaults to HOP_LENGTH.
            window_length (int, optional): window length for spectrogram calculation, typically the same as frame length. Defaults to WINDOW_LENGTH.
            transformation (torchaudio.transforms, optional): transformation function. Defaults to torchaudio.transforms.Spectrogram( n_fft=FRAME_LENGTH, hop_length=HOP_LENGTH, power=2 ).
            feature_func (function, optional): image generation function. Defaults to create_image_spectrogram().
        """
        # assiging parameters
        self.data_dir = data_dir
        self.class_names = class_dir_names.split(" ")
        self.classes = class_dir_names.split(" ")
        self.class_files = []
        self.files_ls = []
        self.sampling_rate = sampling_rate
        self.frame_length = frame_length
        self.hop_length = hop_length
        self.window_length = window_length
        self.transformation = transformation
        self.ctr = 0
        self.class_dict = {}
        self.class_counter = {}
        self.feature_func = feature_func

        # loading filenames into memory
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

    def process(self, idx):
        """takes raw audio files and converts them to spectrograms of TARGET_WINDOW_SIZE_SECONDS and saves them as PyTorch tensors + images of shape (224, 224, 3)

        Args:
            idx (int): file index to process, this follows a PyTorch dataset class' __getitem__() syntax for on the fly generation if necessary
        """
        # get file to process
        curr_file = self.files_ls[idx]

        # load the audio into meory
        data, curr_sampling_rate = torchaudio.load(curr_file)
        # sampling rate is number of samples per second to get to size of interest manipulate target window size value
        bucket_size = curr_sampling_rate * TARGET_WINDOW_SIZE_SECONDS
        # throws away samples that are shorter than TARGET_WINDOW_SIZE_SECONDS * sampling rate
        if len(data[0]) > bucket_size:
            # sliding window over audio file
            prev = 0
            for idx in range(bucket_size, len(data[0]), bucket_size):
                snippet = data[0][prev:idx]
                prev = idx
                # convert current snippet to spectrogram
                input_feature = self._create_feature_representation(
                    snippet, self.feature_func
                )
                # make ResNet-18 input shape (224, 224, 3)
                input_feature = F.pad(input_feature, (2, 2, 2, 2, 0, 0), "constant", 0)
                # squeeze off alpha dimension
                input_feature = torch.squeeze(input_feature, -1)
                # get class label for saving
                for i, val in enumerate(self.class_files):
                    if self.class_dict:
                        if i not in self.class_dict.keys():
                            self.class_dict[i] = self.classes[i]
                    else:
                        self.class_dict[i] = self.classes[i]
                    if curr_file in val:
                        label = i
                        break

                # save tensors
                self._save_tensors(label, input_feature)

    def _create_feature_representation(self, signal, feature_func):
        """convert audio signal to desired visual feature representation

        Args:
            signal (np.ndarray): numpy array sinppet corresponding to audio segment to convert to visual representation

        Returns:
            torch.tensor: returns a PyTorch tensor audio image representation feature
        """
        # apply transformation and create visual representation
        input_feature = self.transformation(signal)
        input_feature = feature_func(input_feature)
        return input_feature

    def _save_tensors(self, label, input_feature):
        """save feature as PyTorch tensor and PNG

        Args:
            label (torch.Tensor): one-hot encoded class label tensor
            input_feature (torch.Tensor): feature tensor of model input shape
        """
        # create save paths for tensor and image
        tensor_save_path = os.path.join(
            TENSOR_OUT_ROOT, self.class_dict[label], str(self.ctr) + ".pt"
        )
        image_save_path = os.path.join(
            IMAGE_OUT_ROOT, self.class_dict[label], str(self.ctr) + ".png"
        )
        # write image
        cv2.imwrite(
            image_save_path,
            cv2.cvtColor(np.moveaxis(input_feature.numpy(), 0, -1), cv2.COLOR_RGB2BGR),
        )

        # this line is unnecessary, but included for explanability
        input_feature = torch.flatten(input_feature)
        # write torch tensor
        torch.save(input_feature, tensor_save_path)

        # filename counter
        self.ctr += 1
