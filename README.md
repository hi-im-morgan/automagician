## Running
Create a virtual enviorment, or at the very least ensure that you have the requirments in the dependencies section of pyproject.toml installed (currently only fabric)

This program is run by simply using the command `automagican` (with any associated flags requested)

Running this script with `python automagician` or other similar command will not work 

## Development
* Create a virtual enviorment using `build.sh create`, and acitvate it using `source .venv/bin/activate`
* Install using `build.sh install_dev`
* Run tests using `build.sh test`
* Run static analyzers/ formatters using `build.sh lint`
## Generating automagician build file
* run `build.sh build` (note that build must be installed)
## Installing from binary
* run `pip install {path_to_binary}`


