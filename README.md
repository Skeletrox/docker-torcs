# Docker-Torcs

## Setup

* Install Docker
* Clone this repository
* Update `docker-compose.yml` to reflect any changes you might want (extra services, port map changes, etc.)
* Make as many copies as you wish in **DIFFERENT** folders and different port mappings (the server internally always runs in port 5000)
* Run `docker-compose up -d` to bring the dockers up
* Run `docker ps -a` to  check status
* Run `docker-compose down` to bring the dockers down
* Run `docker system prune -a` to remove all stopped dockers

## Injecting Logic

* Update `act()` in `app.py` to use your logic and return data the way your learning agent uses. Interface `xvfbwrapper` for any display-related output and processing.
