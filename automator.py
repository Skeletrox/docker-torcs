import os
import shutil

DOCKER_BUILD_DIR = "./DOCKERS"

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

num_dockers = int(input("[+] Enter number of dockers: "))
start_port = int(input("[+] Enter anchor port: "))

try:
    os.makedirs("./{}/".format(DOCKER_BUILD_DIR))
except FileExistsError:
    pass

for i in range(num_dockers):
    folder_name = "{}/torcs_{}".format(DOCKER_BUILD_DIR, i+1)

    try:
        os.makedirs(folder_name)
    except FileExistsError:
        pass

    with open("{}/docker-compose.yml".format(folder_name), 'w+') as d_c:
        d_c.write("version: '3'")
        d_c.write(template_string.format(start_port + i))

    for c in copyables:
        shutil.copyfile("./{}".format(c), "{}/{}".format(folder_name, c))

    print("[*] Docker folder for torcs_{} made".format(i+1))
    