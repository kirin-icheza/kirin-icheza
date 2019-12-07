import tensorflow as tf
import numpy as np
import cv2
from person import BodyPart, KeyPoint, Position, Person

def annotate_img(img, interpreter):
    scaled_image, height_scale, width_scale = scale_image(img) # img scaling
    person = detect_person(scaled_image, interpreter)
    for point in person.key_points:
        if point.score < 0.5: # 50보다 낮은 확률의 신체부위는 표시하지 않음
            continue
        x = int(point.position.x * width_scale) # 신체부위라고 판별 되는 부위 좌표 체크
        y = int(point.position.y * height_scale)
        cv2.circle(img, (x, y), radius=5, color=(255, 0, 0), thickness=-1, lineType=8, shift=0) # img에 점 찍기
    return img

# Load TFLite model and allocate tensors.
def load_model():
    interpreter = tf.lite.Interpreter(model_path='./posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite')
    interpreter.allocate_tensors()
    return interpreter