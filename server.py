from flask import Flask, render_template, Response
import time
import picamera
import cv2
from pose_detector import *

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
    t = 0;
    interpreter = load_model()
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if t == 0:
            overlay_pose = True
        else :
            overlay_pose = False

        # overlay_pose = True이면 추론하고 점찍기
        if overlay_pose:
            img, person, scale = annotate_img(img, interpreter)

        for point in person.key_points:
            if point.score < 0.5:  # 50보다 낮은 확률의 신체부위는 표시하지 않음
                continue
            x = int(point.position.x * scale[1])  # 신체부위라고 판별 되는 부위 좌표 체크
            y = int(point.position.y * scale[0])
            cv2.circle(img, (x, y), radius=5, color=(255, 0, 0), thickness=-1, lineType=8, shift=0)  # img에 점 찍기

        temp, jpeg = cv2.imencode('.jpg', img)
        img = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')

        t = t + 1;
        t = t % 100;

        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(gen(overlay_pose=True), mimetype='multipart/x-mixed-replace; boundary=frame')
        
if __name__ == "__main__":
    app.run(host ='0.0.0.0', port =80, debug=True)