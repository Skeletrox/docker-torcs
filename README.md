# Docker-TORCS

TORCS running in headless mode on Docker.

## Setup

* Install Docker
* Clone this repository
* Run `automator.py`
* The orchestrator is present in the `Orchestrator` folder.

## Injecting Logic

* Update `step()` and `reset()` in `app.py` to use your logic and return data the way your learning agent uses. Interface `xvfbwrapper` for any display-related output and processing.

## Additional Notes

The `Dockerfile` in the root directory of this project is the Dockerfile that will be used for the generated dockers. Make any changes you feel fit on this file.
