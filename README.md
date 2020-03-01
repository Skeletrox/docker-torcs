# Docker-TORCS

TORCS running in headless mode on Docker.

## Setup

* Install Docker
* Clone this repository
* Enter the `ROOT_DOCKER` directory and run `docker build -t torcs_docker .` \(While you can change the name, you will have to change the `FROM` attribute in `automator.py` to reflect the new image name \)
* Run `automator.py` and follow the on-screen instructions.
* The newer docker files will be placed in the `DOCKERS` directory.
* Bring up a docker container in any folder containing `docker-compose.yml` by running `docker-compose up -d`
* Stop containers by running `docker-compose down` and purge data using `docker system prune -a`

## Injecting Logic

* Update `act()` in `app.py` to use your logic and return data the way your learning agent uses. Interface `xvfbwrapper` for any display-related output and processing.

## Additional Notes

The `Dockerfile` in the root directory of this project is the Dockerfile that will be used for the generated dockers. Make any changes you feel fit on this file.
