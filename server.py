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
    interpreter = load_model()
    cam = cv2.VideoCapture(0)
    while True:
        ret_val, img = cam.read()
        if overlay_pose:
            img = annotate_img(img, interpreter)

        temp, jpeg = cv2.imencode('.jpg', img)
        img = jpeg.tobytes()
        yield (b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + img + b'\r\n\r\n')
        if cv2.waitKey(1) == 27:
            break  # esc to quit
    cv2.destroyAllWindows()

@app.route('/video_feed')
def video_feed():
    return Response(gen(overlay_pose=True), mimetype='multipart/x-mixed-replace; boundary=frame')
        
if __name__ == "__main__":
    app.run(host ='0.0.0.0', port =80, debug=True)