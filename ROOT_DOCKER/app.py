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


def execute(cmd, file_descriptor):
    popen = subprocess.Popen(cmd, stdout=file_descriptor, stderr=file_descriptor, universal_newlines=True)


def launch_ffmpeg():
    # get the appropriate display number
    print("Attempting to open FFMPEG:")
    #display_number = None
    #while display_number is None:
    #    z = None
    #    print("Attempting to get display...")
    #    with open('/tmp/displayx', 'rw') as rw:
    #        subprocess.run(["ls", "-a", "/tmp"], stdout=rw)
    #        z = rw.read().decode()
    #    # Xvfb holds a lock in /tmp
    #    finds = findall(r"X(\d+)-lock", z) 
    ##    if len(finds) != 0:
    #       display_number = finds[0]
    #        environ["DISPLAY"] = display_number
    #        print("Display Number is:", display_number)
    #    else:
    #        # try again after 5 seconds
    #        print("FFMPEG: Cannot find display... trying after 5s")
    #        time.sleep(5)
    f2 = open('/var/log/torcs_ffmpeg.log', 'w+')
    try:
        execute("ffmpeg -video_size 640x480 -framerate 25 -f x11grab -i :0.0+0,0 /tmp/output.mp4", f2)
    except Exception as e:
        with open('/var/log/torcs_ffmpeg_err.log', 'a+') as f3:
            f3.write(e)
    f2.close()


def launch_torcs():
    print("Getting display up..")
    environ["DISPLAY"] = ":0"
    vdisplay = Xvfb(width=640, height=480, display="0")
    vdisplay.start()
    while True:
        try:
            f = open('/var/log/torcs_py.log', 'w+')
            execute("/code/torcs-1.3.7/BUILD/bin/torcs", f)
        except Exception as e:
            print(e)            
        finally:
            f.close()
        time.sleep(600)


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