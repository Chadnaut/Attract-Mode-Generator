# Build

How to compile python into executables for distribution.

## Environment

- Nuitka `2.3.9` currently supports Python `3.12.3`
- [pyenv](https://github.com/pyenv/pyenv) | [pyenv for Windows](https://github.com/pyenv-win/pyenv-win) - Manage multiple python versions

```sh
# list available py versions
pyenv install -l

# install version
pyenv install 3.12.3

# set version
pyenv global 3.12.3
```

## Requirements

```sh
# update pip
python -m pip install --upgrade pip

# install project packages
pip install -r requirements.txt
```

The packages will need to be re-installed if you change python versions.

## Compile

```sh
# install / update compiler
python -m pip install -U nuitka

# create executable
python -m nuitka generate.py
```

Additional information can be found on the Nuitka [Tutorial Setup and Build](https://nuitka.net/user-documentation/tutorial-setup-and-build.html) page.

## Results

|Package|Size|
|-|-|
|Numpy|10 MB|
|Python|6 MB|
|Pillow|3 MB|
|Other|1 MB|
|**TOTAL**|**20 MB**|

The final app size is relatively large since pre-compiled package dll's get bundled into the executable, rather than getting tree-shaken / re-built. This results in a lot of dead code, but the end result is much more portable and user friendly.
