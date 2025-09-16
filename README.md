# Automagician
An automation script for Nudged Elastic Band calculations.


## Quick Start Guide
1. Create a virtual environment and activate it.
```
$ ./build.sh create
$ source .venv/bin/activate
```

2. Build automagician \
*Note: you must have `build` installed.* \
*Install it with `python -m pip install build`*
```
$ ./build.sh build
```

3. Run it
```
$ automagician
```

## Development
* Create a virtual environment using `build.sh create`, and activate it using `source .venv/bin/activate` in your `automagician` directory.
* Install using `./build.sh install_dev`
* Run tests using `./build.sh test`
* Run static analyzers/formatters using `./build.sh lint`
## Generating automagician build file
* run `./build.sh build` (note that build must be installed)
## Installing from binary
* run `python -m pip install {path_to_binary}`


