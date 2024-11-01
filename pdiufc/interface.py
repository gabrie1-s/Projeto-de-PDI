import os
import cv2
import json
import time
import socket
import asyncio
import logging
import threading
import numpy as np
from . import processing

from flask import Response
from flask import Flask
from flask import render_template

logging.basicConfig()

serverIP = socket.gethostbyname(socket.gethostname())
lock = threading.Lock()
lock_state = threading.Lock()
app = Flask(__name__)

STATE = {
    'active': False,
    'video_src': '',
    'velocity': 0,
    'input_video': ['webcam'],
    'noise_type': []
}

USERS = set()


class VariablesManager:
    def __init__(self):
        self.lock = threading.Lock()
        # Camera Information
        self.fps = None                 # frames per second
        self.fov = None                 # field of view (deg)
        self.width = None               # camera image width (px)
        self.height = None              # camera image height (px)
        self.camera_distance = None     # distance from camera to conveyor belt (cm)

        # Object Dimensions
        self.object_width = None        # object width (cm)
        self.object_height = None       # object height (cm)

        #luminosidade
        self.lum = None

        self.rotation_threshold = None
        self.xe = None
        self.xd = None

        self._conveyor_width = None
        self._pixels_per_centimeter = None
        self._object_width_px = None
        self._object_height_px = None

    def set_info(self, fps, fov, width, height, camera_dist, lum):
        with self.lock:
            #self.rotation_threshold = float(rth)
            self.fps = int(fps)
            self.fov = int(fov)
            self.width = int(width)
            self.height = int(height)
            self.camera_distance = float(camera_dist)
            self.lum = float(lum)*2 -100

            object_w = 8
            object_h = 5.77
            self._conveyor_width = int(round(2 * float(camera_dist) * np.tan((np.pi / 180 * float(fov)) / 2)))
            self._pixels_per_centimeter = round(int(width) / self._conveyor_width)
            self._object_width_px = round(float(object_w) * self._pixels_per_centimeter)
            self._object_height_px = round(float(object_h) * self._pixels_per_centimeter)

            self.xe = 0
            self.xd = int(self.xe + 1.4*max(self._object_width_px, self._object_height_px))

    def get_info(self, attr):
        with self.lock:
            if hasattr(self, attr):
                return getattr(self, attr)
            else:
                return None

    def convert_velocity_to_cm_s(self, v):
        if self.fps:
            return v*(self.fps/self._pixels_per_centimeter)
        else:
            return 0


VM = VariablesManager()


def process(processed_data, original_image):
    global output_frame

    for t in processed_data['fails']:
        x = int(t[0])
        y = int(t[1])
        w = int(t[2])
        h = int(t[3])
        video_height = VM.get_info('height')

        if y > video_height/2:
            cv2.circle(original_image, (int(x+w/2),video_height-5), 10, (0, 0, 255), -1)
        else:
            cv2.circle(original_image, (int(x+w/2),5), 10, (0, 0, 255), -1)
            
        cv2.rectangle(original_image, (int(x), int(y)), (int(x+w), int(y+h)), (0, 255, 200), 2)

        # cv2.line(original_image, (xe, 0), (xe, height), (0, 255, 0), 2)
        # cv2.line(original_image, (xd, 0), (xd, height), (0, 255, 0), 2)


    with lock:
        output_frame = original_image

    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(notify_state())
    loop.close()


# ###################### WEBSOCKET ######################


def state_event():
    return json.dumps({"type": "state", **STATE})


async def notify_state():
    if USERS:  # asyncio.wait doesn't accept an empty list
        message = state_event()
        await asyncio.wait([user.send(message) for user in USERS])


async def register(websocket):
    USERS.add(websocket)


async def unregister(websocket):
    USERS.remove(websocket)


async def receiver(websocket, _):
    global STATE
    # register(websocket) sends user_event() to websocket
    await register(websocket)
    try:
        await websocket.send(state_event())
        async for message in websocket:
            data = json.loads(message)
            if data["active"]:
                with lock_state:
                    VM.set_info(data['fps'],
                                data['fov'],
                                data['res_w'],
                                data['res_h'],
                                data['dist'],
                                data['lum'])
                    STATE["active"] = True
                    STATE["video_src"] = data["fonte"]
                    STATE["velocity"] = 4
                    STATE["noise_type"] = []
                await notify_state()
            elif not data["active"]:
                with lock_state:
                    STATE["active"] = False
                    STATE["velocity"] = 0
                await notify_state()
            else:
                logging.error("unsupported event: {}", data)
    finally:
        await unregister(websocket)


# ##################### WEB SERVER ######################

image_not_found = cv2.imread(os.path.join( "static", "img", "image-not-found.png"))
output_frame = image_not_found

def generate():
    # grab global references to the output frame and lock variables
    global output_frame, lock

    # loop over frames from the output stream
    while True:
        time.sleep(0.005)
        # wait until the lock is acquired
        with lock:
            # check if the output frame is available, otherwise skip
            # the iteration of the loop
            if output_frame is None:
                continue
            # encode the frame in JPEG format
            (flag, encodedImage) = cv2.imencode(".jpg", output_frame)

            # ensure the frame was successfully encoded
            if not flag:
                continue

        # yield the output frame in the byte format
        yield(b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' +
              bytearray(encodedImage) + b'\r\n')


@app.route("/")
def index():
    # return the rendered template
    return render_template("index.html", serverIP=serverIP)


@app.route("/video_feed")
def video_feed():
    # return the response generated along with the specific media
    # type (mime type)
    return Response(generate(),
                    mimetype="multipart/x-mixed-replace; boundary=frame")


def launch_web_server():
    app.run(host='0.0.0.0', port=5000, debug=False,
            threaded=True, use_reloader=False)
