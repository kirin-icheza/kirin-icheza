import tensorflow as tf
import numpy as np
import cv2
from person import BodyPart, KeyPoint, Position, Person


# img data 표준화 -1 ~ 1
def standardize_image(img):
    mean = 128.0
    std = 128.0
    img_norm = (img - mean) / std
    img_norm = img_norm.astype("float32")
    return img_norm

def resize_image(img, dsize=(257,257)):
    # INTER_AREA interpolation is faster than INTER_CUBIC
    # print('image shape before resize_image ', img.shape) # (480, 640, 3)
    reshaped_img = cv2.resize(img, dsize=dsize, interpolation=cv2.INTER_AREA)
    # print('image shape in resize_image ', reshaped_img.shape) # (257, 257, 3)
    reshaped_img = reshaped_img.reshape(1, 257, 257, 3)
    return reshaped_img

def scale_image(img):
    height, width, _ = img.shape # (480, 640, 3)
    height_scale = height / 257
    width_scale = width / 257
    # print('scale_image height ,width : ', img.shape )

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = resize_image(img) # img = (1, 257, 257, 3)
    img = standardize_image(img) # -1 < img < 1
    return img, height_scale, width_scale



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