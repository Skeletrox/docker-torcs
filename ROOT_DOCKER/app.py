import time
import subprocess
from threading import Thread
from flask import Flask, request, jsonify
from xvfbwrapper import Xvfb
import ray
from sys import exit
# from re import findall
from os import environ
import logging


torcs_display = None


def execute(cmd, file_descriptor=None):
    if file_descriptor is not None:
        popen = subprocess.Popen(cmd, stdout=file_descriptor, stderr=file_descriptor, universal_newlines=True, shell=True)
    else:
        popen = subprocess.Popen(cmd, universal_newlines=True, shell=True)

    return popen


def launch_ffmpeg():
    print("Attempting to open FFMPEG:")
    try:
        execute(["ffmpeg -video_size 640x480 -framerate 25 -f x11grab -i :0.0+0,0 -vf scale=64:64 /tmp/output.mp4"], None)
    except Exception as e:
        with open('/var/log/torcs_ffmpeg_err.log', 'a+') as f2:
            f2.write(str(e))


def launch_torcs():
    global torcs_display
    print("Getting display up..")
    vdisplay = Xvfb(width=640, height=480, display="0")
    vdisplay.start()
    try:
        f = open('/var/log/torcs_py.log', 'w')
        z = execute("/code/torcs-1.3.7/BUILD/bin/torcs &")
    except Exception as e:
        print(e)            
    finally:
        z.wait()
        f.close()



app = Flask(__name__)

# define the simulator function.
def simulate(state, action):

    x = state[0]
    y = state[1]

    badReward = -1000
    goodReward = 1000

    # Got gored by a monster
    if x == 2 and y == 2:
        return state, badReward, True
  
    # Got the treasure
    if x == 2 and y == 0:
        return state, goodReward, True

    if action == 0: # Going Left
        x -= 1
    elif action == 1: # Going Right
        x += 1
    elif action == 2:
        y += 1 # Going down
    else:
        y -= 1 # Going up

    # Define boundary crossing penalties
    reward = 0
    if x < 0:
        x = 0
        reward = badReward
    elif x > 2:
        x = 2
        reward = badReward
    elif y < 0:
        y = 0
        reward = badReward
    elif y > 2:
        y = 2
        reward = badReward
  
    return [x, y], reward, False


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
    state = data["state"]
    action = data["action"]
    # client = Client()
    # state, reward, done, info = client.perform(action)
    nextState, reward, done = simulate(state, action)
    return jsonify({
        "nextState": nextState,
        "reward": reward,
        "done": done,
        "action": action
    })


#@ray.remote
#def actUsingRay(actor):
#    stuff = actor.step.remote()
#    return actor

if __name__ == "__main__":
    try:
        print("Getting TORCS up..")
        thread = Thread(target=launch_torcs)
        thread.start()
        print("TORCS launched. Getting FFMPEG up..")
        time.sleep(1)
        #thread2 = Thread(target=launch_ffmpeg)
        #print("FFMPEG launched.")
        #thread2.start()
    except Exception as e:
        print(e)
        working = False
        print("Error launching torcs/ffmpeg. Please check output.")

    print("Trying to execute: ray start --address={host}:6379".format(host=environ["DOCKER_HOST"]))
    proc = subprocess.call("ray start --address={host}:6379".format(host=environ["DOCKER_HOST"]),
                            shell=True)
    print("subprocess called.")
    retries = 0
    while True and not proc and retries < 50:
        try:
            print("initing ray.")
            ray.init(address="{host}:6379".format(host=environ["DOCKER_HOST"]))
            print("ray inited.")
            break
        except Exception as e:
            retries += 1
            print("Retrying in 5s due to {}...".format(str(e)))
            time.sleep(5)

    print("Host={}, port={}, docker host={}".format(environ["FLASK_RUN_HOST"], environ["FLASK_RUN_PORT"], environ["DOCKER_HOST"]))
    app.run(host="{}".format(environ["FLASK_RUN_HOST"]), port="{}".format(environ["FLASK_RUN_PORT"]))