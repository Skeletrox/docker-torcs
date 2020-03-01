import time
import subprocess
import redis
from threading import Thread
from flask import Flask, request, jsonify
from xvfbwrapper import Xvfb


def launch_torcs():
    while True:
        
        try:
            vdisplay = Xvfb()
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
cache = redis.Redis(host='redis', port=6379)

def get_hit_count():
    retries = 5
    while True:
        try:
            return cache.incr('hits')
        except redis.exceptions.ConnectionError as exc:
            if retries == 0:
                raise exc
            retries -= 1
            time.sleep(0.5)


@app.route('/')
def hello():
    count = get_hit_count()
    return 'Hello World! I have been seen {} times.\n'.format(count)


@app.route('/act', methods=["POST"])
def act():
    data = request.json
    action = int(data["action"])
    # client = Client()
    # state, reward, done, info = client.perform(action)
    return jsonify({
        "action": action,
        "state": "insert serialized state here",
        "done": "insert if done here",
        "info": "insert additional info here"
    })