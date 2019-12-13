from flask import Flask, render_template, Response
import time
import picamera
import cv2
from pose_detector import *
import voice_detector
import threading
from ctypes import *
import os

app = Flask(__name__)

@app.after_request
def add_header(response):
    """
    Add
    headers to both force latest IE rendering engine or Chrome Frame
    and
    also to cache the rendered page for 10 minutes
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

@app.route("/")
def show_video():
    return render_template("main.html")

def gen(overlay_pose=False):
    t1 = threading.Thread(target=voice_detector.main)
    t1.start()
    
    pinNum = 21     #방
    pinNum2 = 20    #화장실
    pinNum3 = 26    #거실

    t = 0   # img 몇개마다 pose 인식을 할건지
    DELAYTIME = 50 # 인식 딜레이 타임 설정
    voice_detector.light = 1 # 0 방 불 꺼짐, 1 방불 켜짐, 2 화장실 불 꺼짐, 3 화장실 불 켜짐, 4 거실 불 꺼짐, 5 거실 불 켜짐

    interpreter = load_model() # posenet 모델을 불러옴
    cam = cv2.VideoCapture(0) # 카메라 클래스 가져옴
    while True:
        ret_val, img = cam.read() # 영상 한 컷
        if t == 0:
            overlay_pose = True
        else :
            overlay_pose = False

        #if overlay_pose:
        #    print('server::',voice_detector.light)
        # overlay_pose = True이면 추론하고 점찍기
        if overlay_pose: #and (voice_detector.light == 1):
            img, person, scale = annotate_img(img, interpreter) # posenet을 통해 포즈 추정
            if detect_sleep(person) == 1: # 포즈가 자고 있다고 판단
                print('카메라를 통해  불을 껐음')
                voice_detector.light = 0
                print('server::', voice_detector.light)
            elif detect_sleep(person) == 2: # 포즈가 사람이 선것으로 판단
                print('사람이 확실히 선것을 인지하여 불을 켜줌')
                voice_detector.light = 1 
                print('server::', voice_detector.light)
            else: # 사람이 있으나 자는지 서있는지 모르므로 변화 없음
                print('카메라 인식을 하나 불이 켜진 상태로 변동이 없음')

        for point in person.key_points: # 사람 포즈 좌표를 파란색 점으로 찍어주기 
            if point.score < 0.5:  # 50보다 낮은 확률의 신체부위는 표시하지 않음
                continue
            x = int(point.position.x * scale[1])  # 신체부위라고 판별 되는 부위 좌표 체크
            y = int(point.position.y * scale[0])
            cv2.circle(img, (x, y), radius=5, color=(255, 0, 0), thickness=-1, lineType=8, shift=0)  # img에 점 찍기

        temp, jpeg = cv2.imencode('.jpg', img) # 웹 화면에 렌더링 하기 위해 
        img = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

        t = t + 1 # 딜레이 타임을 늘려줌
        t = t % DELAYTIME 
        
        dirPath = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'led_module.so') 
        Clib = cdll.LoadLibrary(dirPath)
        if voice_detector.light > 3: # 만약 불이 거실에 대한 경우
            Clib.ledControl(pinNum3,voice_detector.light-4)
        elif voice_detector.light> 1: # 만약 불이화장실에 대한 경우
            Clib.ledControl(pinNum2,voice_detector.light-2)
        else: # 만약 불이 방 불에 대한 경우
            Clib.ledControl(pinNum,voice_detector.light)
        if cv2.waitKey(1) == 27:
            break  # esc to quit

    cv2.destroyAllWindows()

@app.route('/video_feed') # 웹에서 비디오가 출력되는 경우gen()실행
def video_feed():
    return Response(gen(overlay_pose=True), mimetype='multipart/x-mixed-replace; boundary=frame')
        
if __name__ == "__main__":
    voice_detector.light = 1
    app.run(host ='0.0.0.0', port =80, debug=True) # Flask 실행
