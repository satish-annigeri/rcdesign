# `rcdesign`
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/rcdesign"> [![PyPI version shields.io](https://img.shields.io/pypi/v/rcdesign.svg)](https://pypi.python.org/pypi/rcdesign/) [![Documentation Status](https://readthedocs.org/projects/rcdesign/badge/?version=latest)](http://rcdesign.readthedocs.io/?badge=latest) [![PyPI download month](https://img.shields.io/pypi/dm/rcdesign.svg)](https://pypi.python.org/pypi/rcdesign/) [![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

`rcdesign` is a Python package for analysis and design of reinforced concrete sections as per IS&nbsp;456:2000, the Indian Standard code of practice for plain and reinforced concrete.

[Documentation](https://rcdesign.readthedocs.io/en/latest/)

# Installation
## Install from PyPI using `pip`
### Requirements
* Python 3.7+
* numpy
* scipy
* sympy

### Install from PyPI
Create a separate directory and install a virtual environment. Activate the virtual environment and install required packages. On *nix systems, do the following:
```bash
$ mkdir rcd_tutorial
$ cd rcd_tutorial
$ python -m venv .venv
$ .venv/bin/activate
(.venv) $ _
```

On Windows, do the following:
```bash
> mkdir rcd_tutorial
> cd rcd_tutorial
> python -m venv .venv
> .venv\Scripts\activate
> (.venv) > _
```

Install using `pip`
```bash
$ (.venv) pip install -U rcdesign
$ (.venv) python -c "from rcdesign import __version__;print(__version____)
$ 0.4.8
```

Run the two built-in examples problem and study the output.
```bash
$ (.venv) python -m rcdesign
```

## Install from Source on github

### Clone the repository
Choose a suitable directory where you wish to clone the source code from github.  Clone the repository using `git`
```bash
$ git clone https://github.com/satish-annigeri/rcdesign.git
```
When you clone the `rcdesign` repository from github, a new directory named `rcdesign` will be created in the current working directory. Change over to the directory `rcdesign` that is created with the command
```bash
$ cd rcdesign
```
List the directory contents and verify the directory structure.

### Create a virtual environment
Create a virtual environment inside the `rcdesign` directory with the following command
```bash
$ python -m venv .venv
```
Activate the virtual environment with the command
```bash
$ source env/bin/activate
(.venv) $ _
```

For Windows operating system, the command is
```bash
> .venv\Scripts\activate
(.venv) > _
```

### Install required packages
Install required packages into the virtual environment with `pip`
```bash
(.venv) $ pip install -U rcdesign[test]
```
This will install pytest and pytest-cov required to run the tests.

### Run tests

Run the tests with `pytest`
```bash
(.venv) $ pytest tests
```
Check code coverage.
```bash
(.venv) $ pytest --cov=rcdesign tests
```
You can also use `nox` to run the tests. Install `nox` using `pip`, if necessary.
```bash
(.venv) $ pip install nox
(.venv) $ nox
```
When you are done using the virtual environment, you can deactivate it with the command `deactivate` at the command prompt in all operating systems.

## Examples
### Built-in Example
Run the built-in example with the following command.
```bash
(.venv) $ python -m rcdesign
```

### Examples from `tests` Directory
Run the additional examples in the `tests` directory with the following command from the command prompt:
```bash
(.venv) $ python -m tests.example01
(.venv) $ python -m tests.example02
...
(.venv) $ python -m tests.example09
```

### Your Own Example
Refer the [documentation](https://rcdesign.readthedocs.io/en/latest/) to write your own scripts.

## Contribute
Contributions are welcome. Contributions can be in a variety of forms:

1. Bug reports
2. Additional features
3. Documentation
4. Additional examples

## Links
- Documentation: [Documentation](https://rcdesign.readthedocs.io/en/latest/)
- PyPI release: [0.4.8](https://pypi.org/project/rcdesign/)
- Github repository: https://github.com/satish-annigeri/rcdesign

## References
1. IS 456:2000 Indian Standard Code of Practice for Plain and Reinforced Concrete (Fourth Revision), Bureau of Indian Standards, New Delhi, 2000.
2. SP:24 (S&T)-1983 Explanatory Handbook on Indian Standard Code of Practice for Plain and Reinforced Concrete (IS 456:1978), Bureau of Indian Standards, New Delhi, 1984.
3. SP 16:1980 Design Aids for Reinforced Concrete to IS:456-1978, Bureau of Indian Standards, New Delhi, 1980.