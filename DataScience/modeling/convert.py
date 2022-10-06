import os
import onnx
import keras
import tensorflow as tf
import onnxruntime
import numpy as np
import torch
import torch.nn as nn
from onnx2keras import onnx_to_keras

from torchvision.models import resnet18

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

assert os.path.exists(MODEL_STATE_DICT_PATH)

torch_model = resnet18()
num_features = torch_model.fc.in_features
torch_model.fc = nn.Sequential(nn.Linear(num_features, len(CLASSES)))

torch_model.load_state_dict(torch.load(MODEL_STATE_DICT_PATH)["model_state_dict"])
torch_model.eval()

batch_size = 1
dummy_input = torch.randn(batch_size, 3, 224, 224, requires_grad=True)
torch_out = torch_model(dummy_input)

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

assert os.path.exists(ONNX_PATH)

onnx_model = onnx.load(ONNX_PATH)
onnx.checker.check_model(onnx_model)

ort_session = onnxruntime.InferenceSession(ONNX_PATH)

ort_inputs = {ort_session.get_inputs()[0].name: dummy_input.detach().cpu().numpy()}
ort_outs = ort_session.run(None, ort_inputs)

assert np.allclose(
    torch_out.detach().cpu().numpy(), ort_outs[0], rtol=1e-03, atol=1e-05
)

keras_model = onnx_to_keras(
    onnx_model,
    ["input"],
    input_shapes=[dummy_input.squeeze(0).shape],
    verbose=False,
    change_ordering=True,
    name_policy="renumerate",
)

keras_out = keras_model.predict(np.rollaxis(dummy_input.detach().cpu().numpy(), 1, 4))

assert np.allclose(torch_out.detach().cpu().numpy(), keras_out, rtol=1e-03, atol=1e-05)

keras_model.save(KERAS_PATH)
loaded_keras_model = keras.models.load_model(KERAS_PATH)

assert keras_model.get_config() == loaded_keras_model.get_config()

converter = tf.lite.TFLiteConverter.from_saved_model(KERAS_PATH)
tflite_model = converter.convert()

with open(TFLITE_PATH, "wb") as f:
    f.write(tflite_model)

interpreter = tf.lite.Interpreter(model_path=TFLITE_PATH)

interpreter.allocate_tensors()

input_details = interpreter.get_input_details()
output_details = interpreter.get_output_details()

interpreter.set_tensor(
    input_details[0]["index"], np.rollaxis(dummy_input.detach().cpu().numpy(), 1, 4)
)
interpreter.invoke()
tflite_output_data = interpreter.get_tensor(output_details[0]["index"])

assert np.allclose(
    torch_out.detach().cpu().numpy(), tflite_output_data, rtol=1e-03, atol=1e-05
)
