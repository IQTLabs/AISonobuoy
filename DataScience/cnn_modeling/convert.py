# file manipulation
import os

# model loading and conversion
import onnx
import keras
import tensorflow as tf
import onnxruntime
import torch
import torch.nn as nn
from onnx2keras import onnx_to_keras

# data manipulation
import numpy as np

# original model backbone architecture
from torchvision.models import resnet18

# loading and saving contants
MODEL_STATE_DICT_PATH = (
    "/home/achadda/sonobuoy_modeling/tugboat_training_outputs/best.pt"
)

CLASSES = ["tugboat", "no_tugboat"]

ONNX_PATH = (
    "/home/achadda/sonobuoy_modeling/tugboat_training_outputs/sonobuoy_model.onnx"
)

KERAS_PATH = (
    "/home/achadda/sonobuoy_modeling/tugboat_training_outputs/sonobuoy_model_keras"
)

TFLITE_PATH = (
    "/home/achadda/sonobuoy_modeling/tugboat_training_outputs/sonobuoy_model.tflite"
)

# make sure loading-in path exists
assert os.path.exists(MODEL_STATE_DICT_PATH)

# initalize architecture for loading model
torch_model = resnet18()
num_features = torch_model.fc.in_features
torch_model.fc = nn.Sequential(nn.Linear(num_features, len(CLASSES)))

# load saved model
torch_model.load_state_dict(torch.load(MODEL_STATE_DICT_PATH)["model_state_dict"])
torch_model.eval()

# test model prediction
batch_size = 1
dummy_input = torch.randn(batch_size, 3, 224, 224, requires_grad=True)
torch_out = torch_model(dummy_input)

# export PyTorch model to ONNX format
torch.onnx.export(
    model=torch_model,
    args=dummy_input,
    f=ONNX_PATH,
    verbose=False,
    opset_version=10,
    export_params=True,
    do_constant_folding=False,
    input_names=["input"],
    output_names=["output"],
    dynamic_axes={"input": {0: "batch_size"}, "output": {0: "batch_size"}},
)

# check that model was saved
assert os.path.exists(ONNX_PATH)

# load in saved model
onnx_model = onnx.load(ONNX_PATH)
# make sure export occured correctly
onnx.checker.check_model(onnx_model)

# set to evaluation mode
ort_session = onnxruntime.InferenceSession(ONNX_PATH)

# run inference on dummy input
ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.detach().cpu().numpy()}
ort_outs = ort_session.run(None, ort_inputs)

# check to make sure that original PyTorch model inference and exported ONNX model inference are withn a reasonable range
# reasonable range from PyTorch docs: https://pytorch.org/tutorials/advanced/super_resolution_with_onnxruntime.html
assert np.allclose(
    torch_out.detach().cpu().numpy(), ort_outs[0], rtol=1e-03, atol=1e-05
)

# export ONNX model to Keras model
keras_model = onnx_to_keras(
    onnx_model,
    ["input"],
    input_shapes=[dummy_input.squeeze(0).shape],
    verbose=False,
    change_ordering=True,
    name_policy="renumerate",
)

# run inference on dummy input
keras_out = keras_model.predict(np.rollaxis(dummy_input.detach().cpu().numpy(), 1, 4))

# check to make sure that original PyTorch model inference and exported Keras model inference are withn a reasonable range
assert np.allclose(torch_out.detach().cpu().numpy(), keras_out, rtol=1e-03, atol=1e-05)

# save Keras model checkpoint
keras_model.save(KERAS_PATH)

# check that save occured
assert os.path.exists(KERAS_PATH)

# load Keras model from file
loaded_keras_model = keras.models.load_model(KERAS_PATH)

# check that saved Keras model and exported model are the same
assert keras_model.get_config() == loaded_keras_model.get_config()

# Convert from Keras to TensorFlow Lite
converter = tf.lite.TFLiteConverter.from_saved_model(KERAS_PATH)
tflite_model = converter.convert()

# save TensorFlow lite model
with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

# setup TensorFlow lite inference session and load saved model
interpreter = tf.lite.Interpreter(model_path=TFLITE_PATH)
interpreter.allocate_tensors()

# run inference session
input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()
interpreter.set_tensor(
    input_details[0]["index"], np.rollaxis(dummy_input.detach().cpu().numpy(), 1, 4)
)
interpreter.invoke()
tflite_output_data = interpreter.get_tensor(output_details[0]["index"])

# check to make sure that original PyTorch model inference and exported TensorFlow lite model inference are withn a reasonable range
assert np.allclose(
    torch_out.detach().cpu().numpy(), tflite_output_data, rtol=1e-03, atol=1e-05
)

# final check that TensorFlow lite
assert os.path.exists(TFLITE_PATH)

# TODO: containerize this
