from flask import Flask, render_template, Response
import time
import picamera
import cv2
from pose_detector import *
import voice_detector
import threading

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

    t = 0
    DELAYTIME = 25
    voice_detector.light = 1

    interpreter = load_model()
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if t == 0:
            overlay_pose = True
        else :
            overlay_pose = False

        if overlay_pose:
            print('server::',voice_detector.light)
        # overlay_pose = True이면 추론하고 점찍기
        if overlay_pose and (voice_detector.light == 1):
            img, person, scale = annotate_img(img, interpreter)
            if detect_sleep(person):
                print('카메라를 통해  불을 껐음')
                voice_detector.light = 0
                print('server::', voice_detector.light)
            else:
                print('카메라 인식을 하나 불이 켜진 상태로 변동이 없음')
                voice_detector.light = 1
                print('server::', voice_detector.light)

        for point in person.key_points:
            if point.score < 0.5:  # 50보다 낮은 확률의 신체부위는 표시하지 않음
                continue
            x = int(point.position.x * scale[1])  # 신체부위라고 판별 되는 부위 좌표 체크
            y = int(point.position.y * scale[0])
            cv2.circle(img, (x, y), radius=5, color=(255, 0, 0), thickness=-1, lineType=8, shift=0)  # img에 점 찍기

        temp, jpeg = cv2.imencode('.jpg', img)
        img = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

        t = t + 1
        t = t % DELAYTIME

        if cv2.waitKey(1) == 27:
            break  # esc to quit

    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(gen(overlay_pose=True), mimetype='multipart/x-mixed-replace; boundary=frame')
        
if __name__ == "__main__":
    voice_detector.light = 1
    app.run(host ='0.0.0.0', port =80, debug=True)
