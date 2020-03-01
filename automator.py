import os
import shutil
import subprocess
import logging
from sys import exit

# The directory where all the docker files will be placed
DOCKER_BUILD_DIR = "DOCKERS"

# Files that will be copied from the current folder to the target folders.
copyables = [
    "Dockerfile",
]

# The docker-compose template string that will be dynamically populated.
template_string = '''
services:
    instance:
        build: .
        ports:
            - "{}:5000"
'''

# A helper function to allow for immediate STDOUT from long-running processing
def execute(cmd):
    popen = subprocess.Popen(cmd, stdout=subprocess.PIPE, universal_newlines=True)
    for stdout_line in iter(popen.stdout.readline, ""):
        yield stdout_line 
    popen.stdout.close()
    return_code = popen.wait()
    if return_code:
        raise subprocess.CalledProcessError(return_code, cmd)

# Number of dockers to bring up
num_dockers = int(input("[+] Enter number of dockers: "))

# The "start" port to anchor from. Dockers interface ports n, n+1, n+2... from the host machine.
start_port = int(input("[+] Enter anchor port: "))


curr_directory = os.getcwd()

# Optional build of the image. Not necessary if images already exist.
if (input("Do you wish to build the docker image? [y/N]: ").upper() == 'Y'):
    os.chdir("{}/ROOT_DOCKER/".format(curr_directory))
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