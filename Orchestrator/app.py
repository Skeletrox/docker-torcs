import time
import subprocess
from flask import Flask, request, jsonify
import json
import requests
from ray_actor import Actor, something
import ray
from sys import exit


app = Flask(__name__)

metadata = None
with open('./config.json') as config:
    metadata = json.loads(config.read())

DOCKER_URL = "http://127.0.0.1"


actors = None

proc = subprocess.call("ray start --head --redis-port=6379",
                            shell=True)


ray.init(address="127.0.0.1:6379")

if proc:
    print("Cannot bring up ray")
    exit(1)

@app.route('/')
def hello():
    return 'Hello World! Visit <a href="https://skeletrox.github.io">skeletrox.github.io</a>!\n'

@app.route('/init', methods=["POST"])
def init():
    data = request.json
    numActors = data["actors"]
    actors = [Actor() for i in range(actors)]

@app.route('/steps', methods=["POST"])
def demux():

    data = request.json
    ports = metadata["containers"]
    returnable = []

    for i in range(len(ports)):
        r = requests.post(url="{}:{}/step".format(DOCKER_URL, ports[i]), json={
            "actions": data["actions"][i]
        })
        print(r.text)
        returnable.append(r.json())

    return jsonify({
        "responses": returnable
    })


@app.route('/raysteps', methods=["POST"])
def demux_ray():
    data = request.json
    returnable = []

    for i in range(len(ports)):
        actors[i].setNextSteps(data["actions"][i])

    return jsonify({
        "responses": returnable
    })


@app.route('/test')
def test():
    result = list(set(ray.get([something.remote() for _ in range(1000)])))
    return jsonify({
        "result": result
    })


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)