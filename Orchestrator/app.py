import time
import subprocess
from flask import Flask, request, jsonify
import json
import requests
from ray_actor import Actor


app = Flask(__name__)

metadata = None
with open('./config.json') as config:
    metadata = json.loads(config.read())

DOCKER_URL = "http://192.168.99.100"


actors = None

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


@app.route('./raysteps', methods=["POST"])
def demux_ray():
    data = request.json
    returnable = []

    for i in range(len(ports)):
        actors[i].setNextSteps(data["actions"][i])

    return jsonify({
        "responses": returnable
    })
