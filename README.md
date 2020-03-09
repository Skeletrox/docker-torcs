# Docker-TORCS

TORCS running in headless mode on Docker with a `flask` and `ray` interface.

## Setup

* Install Docker
* Clone this repository
* Run `automator.py`
* The orchestrator is present in the `Orchestrator` folder.

## Injecting Logic

* Update `step()` and `reset()` in `app.py` to use your logic and return data the way your learning agent uses. Interface `xvfbwrapper` for any display-related output and processing.

* By default `ffmpeg` captures the X11 output and stores it in `/tmp/output.mp4`.

## Additional Notes

* `Dockerfile` and `Dockerfile_orchestrator` are example configs of the dockerfiles that will be used.
* This uses a custom patch of `xvfbwrapper` and is therefore defined as a separate repository in `requirements.txt`
