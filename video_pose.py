import numpy as np
import tensorflow as tf
import cv2

class VideoCamera(object):
    def __init__(self):
       
        # Load TFLite model and allocate tensors.
        self.t = 0;
        self.interpreter = tf.lite.Interpreter(model_path="posenet_mobilenet_v1_100_257x257_multi_kpt_stripped.tflite")
        self.interpreter.allocate_tensors()

        # Get input and output tensors.
        self.input_details = self.interpreter.get_input_details()
        self.output_details = self.interpreter.get_output_details()

        # Test model on random input data.
        self.input_shape = self.input_details[0]['shape']
        #print("Model input_details = ", self.input_details) # [{'name': 'sub_2', 'index': 93, 'shape': array([  1, 257, 257,   3]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]
        #print("Model output_details = ", self.output_details) # [{'name': 'MobilenetV1/heatmap_2/BiasAdd', 'index': 87, 'shape': array([ 1,  9,  9, 17]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/offset_2/BiasAdd', 'index': 90, 'shape': array([ 1,  9,  9, 34]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/displacement_fwd_2/BiasAdd', 'index': 84, 'shape': array([ 1,  9,  9, 32]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}, {'name': 'MobilenetV1/displacement_bwd_2/BiasAdd', 'index': 81, 'shape': array([ 1,  9,  9, 32]), 'dtype': <class 'numpy.float32'>, 'quantization': (0.0, 0)}]
        print("Model Input shape = ", self.input_shape)

        self.cap = cv2.VideoCapture(0) # 비디오 화면 세팅(가로640, 세로480), 인덱스는 어떤 카메라를 쓰는지 명시
        print('video size : width: {}, height : {}'.format(self.cap.get(3), self.cap.get(4)))
        self.cap.set(3,640) # set Width
        # 193, 449
        self.cap.set(4,480) # set Height 240 + 128
        # 117, 356
        #print('width: {}, height : {}'.format(cap.get(3), cap.get(4)))

    def __del__(self):
        self.cap.release()
        #cv2.destroyAllWindows()

    def get_frame(self):
        self.ret, self.frame = self.cap.read()
        #frame = cv2.flip(frame, 0) # Flip camera vertically
        #gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        #프레임 사이즈 조정 (비디오 화면의 중앙부분만 사용, tensor에 input_data 사이즈가 정해져 있기 때문에..)
        self.frame = (self.frame[193:450, 111:368])
        #print(frame)  # frame은 (257, 257, 3) 모양의 numpy 배열
        
        if self.t % 100 == 0 :
            self.reshape_frame = np.array(self.frame, dtype=np.float32)
            self.input_data = np.reshape(self.reshape_frame, [1, self.frame.shape[0], self.frame.shape[1], self.frame.shape[2]])
            print("Input shape = ", self.input_data.shape) # input_data는 (1, 257, 257, 3) 모양의 numpy 배열
            self.interpreter.set_tensor(self.input_details[0]['index'], self.input_data) # 모델에 우리의 input_data 넣기

            self.interpreter.invoke()

            # The function `get_tensor()` returns a copy of the tensor data.
            # Use `tensor()` in order to get a pointer to the tensor.
            self.output_data = self.interpreter.get_tensor(self.output_details[1]['index']) # output 4개중의 어떤 output을 사용할지에 따라 첫번째 인덱스가 달라진다
            print("Output shape = ", self.output_data.shape) # 쓸 output data shape 확인하기
            #self.output_data = np.reshape(np.array(self.output_data, dtype=np.uint8), self.output_data.shape[1:])
            print(self.output_data[0][0][0])
        
        self.t = self.t + 1;
        #cv2.imshow('frame', self.frame)
        #cv2.imshow('gray', gray)\
        #k = cv2.waitKey(30) & 0xff
        #if k == 27: # press 'ESC' to quit
        #    break
        temp, jpeg = cv2.imencode('.jpg', self.frame)
        return jpeg.tobytes()

