## Setup python virtual environment and activate

```shell
- ***MUST*** being run from inside root project directory
```shell
uv venv
uv pip install -e '.[tests]'
# Use OS specific command below
.venv\scripts\activate     # Windows
source .venv/bin/activate  # Linux/MacOS

## Build and start docker image for ssh testing
- ***MUST*** being run from inside `testing` directory
```shell
docker build . -t shinylive-test
docker run --rm -p 2222:22 -p 5001:5001 shinylive-test
```
- A new terminal/powershell window will need to be opened for the steps below

## Run commands to accept and cache ssh key
1. Manually run shinylive_deploy within testing directory
- ***MUST*** being run from inside `testing` directory
```shell
git init .  # <- this creates a .git session with `testing`; gets removed when unitests run
shinylive-manage deploy test
```
- Input password when prompted: docker
- Accept key if when prompted
  - If continued issues with the key are encountered:
    - `ssh shinylive@127.0.0.1 -p 2222` | password: `docker`
    - Accept key when prompted
    - Try `shinylive-manage deploy test` again

## FINALLY, run unit tests
```shell
pytest test -vv -x
```
- If you encounter the `ACTION REQUIRED shinyapps not found in ssh targat`, simply try running the command again. There is code to create this directory, but the a location, only in tests (not the actual app), where it can see that before it checks for its existence. Hopefully will return to this at some point.

## To kill docker container
- This is a quick, bareboes container built just for ssh testing, it has to be killed in a different terminal session to stop it
- Get container ID: `docker ps`
- Stop using ID: `docker stop <ID>`
- After a short period of time it should stop