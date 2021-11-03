# Installation
## From PyPI using `pip`
Create a separate directory and install a virtual environment. Activate the virtual environment and install required packages. On *nix systems, do the following:
```bash
$ mkdir rcd_tutorial
$ cd rcd_tutorial
$ python -m venv ./venv
$ ./venv/bin/activate
$ python -m pip install -U pip
$ pip install rcdesign numpy sympy scipy
$ python -m rcdesign.example
```

On Windows, do the following:
```bash
> mkdir rcd_tutorial
> cd rcd_tutorial
> python -m venv venv
> venv\Scripts\activate
> python -m pip install -U pip
> pip install rcdesign numpy sympy scipy
> python -m rcdesign.example
```

If installation is successful, the example problem must run and you should see the output.

## Clone github Repository
If you want to play with the source code, you can clone the github repository wwith `git`.
```bash
$ git clone https://github.com/satish-annigeri/rcdesign.git
```
This creates the directory `rcdesign` in the current working directory. You should then proceed to create a virtual environment, activate it and install the required packages before starting to work with the source code.

### Compile documentation
If you wish to compile the documentation, you must install the `sphinx` package and compile the documentation with the `make html` command from the `./rcdesign/docs` directory and browse the documentation in the `./rcdesign/docs/build/html` directory.