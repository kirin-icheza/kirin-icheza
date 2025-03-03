import tensorflow as tf
import numpy as np
import cv2
from person import BodyPart, KeyPoint, Position, Person

def sigmoid(x): # 시그모이드 취하기
    return 1/(1+np.exp(-x))

def load_image(img='./static/img.png'): # cv2저장된 이미지 로드
    return cv2.imread(img)

# img data 표준화 -1 ~ 1
def standardize_image(img): 
    mean = 128.0
    std = 128.0
    img_norm = (img - mean) / std
    img_norm = img_norm.astype("float32")
    return img_norm

def resize_image(img, dsize=(257,257)): # 포즈넷은 257*257을 입력으로 받음
    # INTER_AREA interpolation is faster than INTER_CUBIC
    # print('image shape before resize_image ', img.shape) # (480, 640, 3)
    reshaped_img = cv2.resize(img, dsize=dsize, interpolation=cv2.INTER_AREA)
    # print('image shape in resize_image ', reshaped_img.shape) # (257, 257, 3)
    reshaped_img = reshaped_img.reshape(1, 257, 257, 3)
    return reshaped_img

def scale_image(img): # 나중에 이미지 키울때를 대비해 포즈넷 입력과 이미지 입력 크기 비교
    height, width, _ = img.shape # (480, 640, 3)
    height_scale = height / 257
    width_scale = width / 257
    # print('scale_image height ,width : ', img.shape )

    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = resize_image(img) # img = (1, 257, 257, 3)
    img = standardize_image(img) # -1 < img < 1
    return img, height_scale, width_scale

def detect_person(img, interpreter) -> Person: # img를 posenet에 통과시킴
    # Get input and output tensors.
    input_details = interpreter.get_input_details() # [{'name': 'sub_2', 'index': 93, 'shape': array([  1, 257, 257,   3]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]
    output_details = interpreter.get_output_details() # [{'name': 'MobilenetV1/heatmap_2/BiasAdd', 'index': 87, 'shape': array([ 1,  9,  9, 17]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/offset_2/BiasAdd', 'index': 90, 'shape': array([ 1,  9,  9, 34]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/displacement_fwd_2/BiasAdd', 'index': 84, 'shape': array([ 1,  9,  9, 32]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/displacement_bwd_2/BiasAdd', 'index': 81, 'shape': array([ 1,  9,  9, 32]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]
    input_shape = input_details[0]['shape']

    interpreter.set_tensor(input_details[0]['index'], img)
    interpreter.invoke()

    heatmaps = interpreter.get_tensor(output_details[0]['index'])
    offsets = interpreter.get_tensor(output_details[1]['index'])
    _, height, width, n_keypoints = heatmaps.shape

    keypoint_positions = {} # 0 ~ 17번 히트맵 신체 위치의 좌표
    for i in range(heatmaps.shape[-1]): # 키포인트 만큼 반복
        heatmaps[0, ..., i] = sigmoid(heatmaps[0, ..., i])
        hm = heatmaps[0, ..., i]
        max_row, max_col = np.where(hm == np.max(hm)) # 히트맵에서 가장 큰값의 행 열을 리턴
        keypoint_positions[i] = (max_row[0], max_col[0])

    y_coords = {} # 실제 신체 좌표가 된다
    x_coords = {}
    confidence_scores = {} # 각 히트맵 최고점의 신뢰 확률

    for idx, v in keypoint_positions.items(): # key(index), value  몸의 각 위치를 저장해두고 신뢰도 저장
        position_y = v[0]
        position_x = v[1]
        y_coords[idx] = int((position_y / float(height-1)) * 257 + offsets[0][position_y][position_x][idx]) # 오프셋을 더한 실제 신체위치의 좌표
        x_coords[idx] = int((position_x / float(width-1)) * 257 + offsets[0][position_y][position_x][idx + n_keypoints]) # 오프셋 배열은 17개의 행에대환 오프셋 이후 17개의 열에대한 오프셋을 제공
        confidence_scores[idx] = heatmaps[0][position_y][position_x][idx]

    total_score = 0
    key_points = []
    for idx, b in enumerate(BodyPart): # PERSON 클라스 객체에 필요한 정보들을 구해준다
        position = Position(x=x_coords[idx], y=y_coords[idx])
        key_points.append(KeyPoint(body_part=b, position=position, score=confidence_scores[idx]))
        total_score += confidence_scores[idx]

    p = Person(key_points, score=total_score/n_keypoints) # Person 객체 생성후 리턴
    return p

def annotate_img(img, interpreter): # 추론을 진행하고 이미지에 점찍기
    scaled_image, height_scale, width_scale = scale_image(img) # img scaling
    person = detect_person(scaled_image, interpreter)
    scale = [height_scale, width_scale]
    for point in person.key_points:
        if point.score < 0.5: # 50보다 낮은 확률의 신체부위는 표시하지 않음
            continue
        x = int(point.position.x * width_scale) # 신체부위라고 판별 되는 부위 좌표 체크
        y = int(point.position.y * height_scale)
        cv2.circle(img, (x, y), radius=5, color=(255, 0, 0), thickness=-1, lineType=8, shift=0) # img에 점 찍기
    return img, person, scale

 # Load TFLite model and allocate tensors.
def load_model():
    interpreter = tf.lite.Interpreter(model_path='./posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite')
    interpreter.allocate_tensors()
    return interpreter

def detect_sleep(person): # person 객체 정보를 통해 잠을자는지 일어섰는지 등을 확인 리턴
    i = 0
    flag_up = 0
    flag_down = 0
    upper_body = [0, 0]
    lower_body = [0, 0]
    for point in person.key_points:
        i = i + 1
        if point.score < 0.3:  # 50보다 낮은 확률의 신체부위는 무시
            continue
        if i >= 12 and point.score > flag_down: # 하반신인 경우
            lower_body[0] = int(point.position.x)
            lower_body[1] = int(point.position.y)
            flag_down = point.score
        elif i <= 7 and point.score > flag_up: # 상반신의 경우
            upper_body[0]= int(point.position.x)
            upper_body[1]= int(point.position.y)
            flag_up = point.score
    if (not flag_up and not flag_down) == 1:
        return 1
    if abs(upper_body[0] - lower_body[0]) == 0:
        return 0
    if flag_up and flag_down and abs(upper_body[1] - lower_body[1]) / abs(upper_body[0] - lower_body[0]) < 1:
        return 1
    if flag_up and flag_down and abs(upper_body[1] - lower_body[1]) / abs(upper_body[0] - lower_body[0]) > 1:
        return 2
    return 0
