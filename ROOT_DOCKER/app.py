import time
import subprocess
from threading import Thread
from flask import Flask, request, jsonify
from xvfbwrapper import Xvfb
import ray
from sys import exit


def launch_ffmpeg():
    y = subprocess.check_output(
        ["ffmpeg -video_size 640x480 -framerate 25 -f x11grab -i :0.0+0,0 /tmp/output.mp4"],
        shell=True
    )
    print("FFMPEG output:", y.decode())


def launch_torcs():
    while True:
        z = subprocess.check_output(
            ["/code/torcs-1.3.7/BUILD/bin/torcs"],
            shell=True
        )
        print("TORCS output:", z.decode())
        time.sleep(600)


try:
    working = True
    vdisplay = Xvfb(width=640, height=480)
    vdisplay.start()
    thread = Thread(target=launch_torcs)
    thread.start()
    thread2 = Thread(target=launch_ffmpeg)
    thread2.start()
except:
    working = False
    print("Error launching torcs/ffmpeg. Please check output.")
finally:
    vdisplay.stop()
    if not working:
        exit(1)

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Hello World! Visit <a href="https://skeletrox.github.io">skeletrox.github.io</a>!\n'


@app.route('/reset')
def reset():
    # Reset the environment
    pass


@app.route('/step', methods=["POST"])
def act():
    data = request.json
    actions = data["actions"]
    # client = Client()
    # state, reward, done, info = client.perform(action)
    return jsonify({
        "actions": actions,
        "state": "insert serialized state here",
        "done": "insert if done here",
        "info": "insert additional info here"
    })


@ray.remote
def actUsingRay(actor):
    stuff = actor.step.remote()
    return actor