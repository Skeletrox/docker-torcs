import os
import shutil
import subprocess
import logging
from sys import exit

DOCKER_BUILD_DIR = "DOCKERS"

copyables = [
    "Dockerfile",
]

template_string = '''
services:
    instance:
        build: .
        ports:
            - "{}:5000"
'''

def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)


num_dockers = int(input("[+] Enter number of dockers: "))
start_port = int(input("[+] Enter anchor port: "))

curr_directory = os.getcwd()

os.chdir("{}/ROOT_DOCKER/".format(curr_directory))
if (input("Do you wish to build the docker image? [y/N]: ").upper() == 'Y'):
    print("Building image...")
    for line in execute(["docker", "build", "-t", "torcs_docker", "."]):
        print(line,end="")

try:
    os.makedirs("{}/{}/".format(curr_directory, DOCKER_BUILD_DIR))
except FileExistsError:
    pass

for i in range(num_dockers):
    folder_name = "{}/{}/torcs_{}".format(curr_directory, DOCKER_BUILD_DIR, i+1)

    try:
        os.makedirs(folder_name)
    except FileExistsError:
        pass

    with open("{}/docker-compose.yml".format(folder_name), 'w+') as d_c:
        d_c.write("version: '3'")
        d_c.write(template_string.format(start_port + i))

    for c in copyables:
        shutil.copyfile("{}/{}".format(curr_directory, c), "{}/{}".format(folder_name, c))

    print("[*] Docker folder for torcs_{} made".format(i+1))


print("[*] Bringing dockers up...")

for i in range(num_dockers):
    os.chdir("{}/{}/torcs_{}".format(curr_directory, DOCKER_BUILD_DIR, i+1))
    for line in execute(["docker-compose", "up", "-d"]):
        print(line, end="")
    print("Docker torcs_{} up. Events logged.".format(i+1))