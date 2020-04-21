import time
import subprocess
from flask import Flask, request, jsonify
import json
import requests
from os import environ
from ray_actor import Actor, something
import ray
import random
import asyncio
import aiohttp
from sys import exit


app = Flask(__name__)

metadata = None
with open('./config.json') as config:
    metadata = json.loads(config.read())

DOCKER_URL = "http://{}".format(environ["DOCKER_HOST"])

actors = None

import random
import string

# Random string generator to uniquely identify each docker instance
def randomString(stringLength=8):
    letters = string.ascii_lowercase
    return "".join([random.choice(letters) for i in range(stringLength)])


async def fetchJson(session, url, jsonData=None, method=None):
    if method == "POST":
        async with session.post(url, json=jsonData) as response:
            return await response.text()
    else:
        async with session.get(url) as response:
            return await response.text()


async def rollCallAsync():
    tasks = []
    ports = metadata["containers"]
    for i in range(len(ports)):
        session = aiohttp.ClientSession()
        url = "{}:{}/getname".format(DOCKER_URL, ports[i])
        tasks.append(fetchJson(session, url))

    res = await asyncio.gather(*tasks, return_exceptions=True)
    return res


async def demuxSteps(data):
    ports = metadata["containers"]
    tasks = []
    sessions = []
    for i in range(len(ports)):
        session = aiohttp.ClientSession()
        jsonData = {
            "state": data["states"][i],
            "action": data["actions"][i]
        }
        url = "{}:{}/step".format(DOCKER_URL, ports[i])

        # r = requests.post(url="{}:{}/step".format(DOCKER_URL, ports[i]), json={
        #     "state": data["states"][i],
        #     "action": data["actions"][i]
        # })
        tasks.append(fetchJson(session, url, jsonData, "POST"))
        sessions.append(session)
    res = await asyncio.gather(*tasks, return_exceptions=True)
    for session in sessions:
        await session.close()
    return res
        



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


@ray.remote
def nexus():
    return {
        "ID": environ["TORCS_ID"]
    }


@app.route('/')
def hello():
    return 'Hello World! Visit <a href="https://skeletrox.github.io">skeletrox.github.io</a>!\n'


@app.route('/steps', methods=["POST"])
def demux():
    print("Here")
    data = request.json
    print("Then")
    returnable = {}
    print("I came")
    loop = asyncio.new_event_loop()
    print("What if")
    asyncio.set_event_loop(loop)
    print("There was none")
    returnable = asyncio.get_event_loop().run_until_complete(demuxSteps(data))
    print("That could tell me what I could do")
    print("returnable is", returnable)
    return jsonify({
        "responses": returnable
    })

@app.route('/init')
def initWorkers():
    ports = metadata["containers"]
    returnable = {}
    for i in range(len(ports)):
        value = randomString()
        r = requests.post(url="{}:{}/setname".format(DOCKER_URL, ports[i]), json={
             "id": value
        })
        returnable[value] = r.json()


    return jsonify({
        "responses": returnable
    })


@app.route('/rollcall')
def rollCall():
    print("Rollcalling...")
    loop = asyncio.new_event_loop()
    print("Loop defined.")
    asyncio.set_event_loop(loop)
    print("Event loop set.")
    returnable = asyncio.get_event_loop().run_until_complete(rollCallAsync())
    print("Returnable obtained.")
    return jsonify({
        "responses": [str(r) for r in returnable]
    })


@app.route('/drives')
def drives():
    ports = metadata["containers"]
    returnable = {}
    for i in range(len(ports)):
        r = requests.get(url="{}:{}/drive".format(DOCKER_URL, ports[i]))
        returnable[i] =  r.json()

    return jsonify({
        "responses": returnable
    })


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