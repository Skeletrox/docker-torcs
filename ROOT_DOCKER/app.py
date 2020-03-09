import time
import subprocess
from threading import Thread
from flask import Flask, request, jsonify
from xvfbwrapper import Xvfb
import ray
from sys import exit
from re import findall
from os import environ
import logging


def execute(cmd, file_descriptor=None):
    if file_descriptor is not None:
        popen = subprocess.Popen(cmd, stdout=file_descriptor, stderr=file_descriptor, universal_newlines=True, shell=True)
    else:
        popen = subprocess.Popen(cmd, universal_newlines=True, shell=True)

    return popen


def launch_ffmpeg():
    print("Attempting to open FFMPEG:")
    try:
        execute(["ffmpeg -video_size 640x480 -framerate 25 -f x11grab -i :0.0+0,0 /tmp/output.mp4"], None)
    except Exception as e:
        with open('/var/log/torcs_ffmpeg_err.log', 'a+') as f2:
            f2.write(str(e))


def launch_torcs():
    print("Getting display up..")
    vdisplay = Xvfb(width=640, height=480, display="0")
    vdisplay.start()
    try:
        f = open('/var/log/torcs_py.log', 'w')
        z = execute("/code/torcs-1.3.7/BUILD/bin/torcs", f)
    except Exception as e:
        print(e)            
    finally:
        z.wait()
        f.close()


try:
    print("Getting TORCS up..")
    thread = Thread(target=launch_torcs)
    thread.start()
    print("TORCS launched. Getting FFMPEG up..")
    time.sleep(1)
    thread2 = Thread(target=launch_ffmpeg)
    print("FFMPEG launched.")
    thread2.start()
except Exception as e:
    print(e)
    working = False
    print("Error launching torcs/ffmpeg. Please check output.")

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