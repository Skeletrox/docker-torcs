import time
import subprocess
from threading import Thread
from flask import Flask, request, jsonify
from xvfbwrapper import Xvfb
import ray


def launch_torcs():
    while True:
        
        try:
            vdisplay = Xvfb(width=640, height=480)
            vdisplay.start()
            z = subprocess.Popen(
                ["/code/torcs-1.3.7/BUILD/bin/torcs"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            print("STDOUT:", z.stdout)
            print("STDERR:", z.stderr)
            time.sleep(600)
        finally:
            vdisplay.stop()

try:
    thread = Thread(target=launch_torcs)
    thread.start()
except:
    print("FAIL")

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