import tensorflow as tf
import numpy as np
import cv2
from person import BodyPart, KeyPoint, Position, Person

# Load TFLite model and allocate tensors.
def load_model():
    interpreter = tf.lite.Interpreter(model_path='./posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite')
    interpreter.allocate_tensors()
    return interpreter