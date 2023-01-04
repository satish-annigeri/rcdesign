# Installation
## Install from PyPI using `pip`
### Requirements
* Python 3.7+
* numpy
* scipy
* sympy

### Install
Create a separate directory and install a virtual environment. Activate the virtual environment and install required packages. On *nix systems, do the following:
``` console
$ mkdir rcd_tutorial
$ cd rcd_tutorial
$ python -m venv ./venv
$ ./venv/bin/activate
$ python -m pip install -U pip
$ pip install rcdesign numpy sympy scipy
$ python -m rcdesign.example
```

On Windows, do the following:
``` console
> mkdir rcd_tutorial
> cd rcd_tutorial
> python -m venv venv
> venv\Scripts\activate
> python -m pip install -U pip
> pip install rcdesign numpy sympy scipy
> python -m rcdesign.example
```

If installation is successful, the example problem must run and you should see the output.

## Install from Source on github
To install from github, you can clone the github repository and give it a try. If you are not familiar with the workflow for working with a source repository, you can follow the steps below.

### Preliminary checks
Check the version of Python you are using. You will require version 3.7 or later. To print the version of Python, use the command
``` console
$ python -V
Python 3.9.7
```
On a *nix system, you may have to type
``` console
$ python3 -V
Python 3.9.7
```

### Clone the repository
When you clone the `rcdesign` repository from github, a new directory named `rcdesign` will be created in the current working directory. Therefore change over to the a suitable directory which will become the parent directory of the clone. Clone the repository using `git`
``` console
$ git clone https://github.com/satish-annigeri/rcdesign.git
```

Change over to the directory `rcdesign` that is created with the command
``` console
$ cd rcdesign
```
List the directory contents and verify the directory structure.

### Create a virtual environment
Create a virtual environment inside the `rcdesign` directory with the following command
``` console
$ python -m venv env
```
Activate the virtual environment with the command
``` console
$ source env/bin/activate
(env) $_
```

If you are using Windows operating system, the command is
``` console
> env\Scripts\activate
(env) >_
```
Update `pip` with the command
``` console
(env) $ python -m pip install -U pip
```
### Install required packages
Install required packages into the virtual environment with `pip`
``` console
(env) $ pip install -r requirements.txt
```
### Run tests
Install additional packages required to run tests.
``` console
(env) pip install pytest pytest-cov nox
```
Run the tests with `pytest`
``` console
(env) $ pytest tests
```
Check code coverage.
``` console
(env) $ pytest --cov=rcdesign tests/
```
You can also use `nox` to run the tests.
``` console
(env) $ nox
```

### Examples from `tests` Directory
Run the examples in the `tests` directory with the following command from the command prompt:
```bash
(env) $ python -m tests.example00
(env) $ python -m tests.example01
...
(env) $ python -m tests.example09
```

When you are done using the virtual environment, you can deactivate with the command `deactivate` at the command prompt in all operating systems.
