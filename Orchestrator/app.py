import time
import subprocess
from flask import Flask, request, jsonify
import json
import requests
from os import environ
from ray_actor import Actor, something
import ray
import random
from sys import exit


app = Flask(__name__)

metadata = None
with open('./config.json') as config:
    metadata = json.loads(config.read())

DOCKER_URL = "http://{}".format(environ["DOCKER_HOST"])


actors = None

@ray.remote
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

@app.route('/init', methods=["POST"])
def init():
    data = request.json
    numActors = data["actors"]
    actors = [Actor() for _ in range(actors)]

@app.route('/steps', methods=["POST"])
def demux():

    data = request.json
    ports = metadata["containers"]
    returnable = {}

    for i in range(len(ports)):
        r = requests.post(url="{}:{}/step".format(DOCKER_URL, ports[i]), json={
            "state": data["states"][i],
            "action": data["actions"][i]
        })
        returnable[i] =  r.json()

    return jsonify({
        "responses": returnable
    })



#@app.route('/raysteps', methods=["POST"])
#def demux_ray():
#    data = request.json
#    returnable = []
#
#    for i in range(len(ports)):
#        actors[i].setNextSteps(data["actions"][i])
#
#    return jsonify({
#        "responses": returnable
#    })


@app.route('/test', methods=['POST'])
def test():
    print("Request:")
    print(request)
    data = request.json
    print("Data:")
    print(data)
    num_states = len(data.get("states", []))
    num_actions = len(data.get("actions", []))
    if num_states != num_actions:
        return jsonify({
            "error": "Improper data"
        })

    result = list([ray.get(simulate.remote(data["states"][i], data["actions"][i])) for i in range(num_states)])
    return jsonify({
        "result": result
    })


if __name__ == "__main__":
    proc = subprocess.call("ray start --head --redis-port=6379", shell=True)
    if proc:
        print("Cannot bring up ray. Check logs.")
        exit(1)
    
    ray.init(address="127.0.0.1:6379")
    print("ray initialized.")
    app.run(host="0.0.0.0", port=5000)