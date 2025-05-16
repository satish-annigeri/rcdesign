# Installation
## Install from PyPI using `pip`

This is when you only wish to use `rcdesign` without attempting to look at its source code, documentation on your local machine or wishing to run tests.

The traditional way is to install `rcdesign` from PyPI using `pip` into a previously created virtual environment and write your scripts to use the package. The other way is to use `uv` to create the virtual environment and install `rcdesign` from PyPI using `uv`. The former approcah is good enough if you merely wish to use the package, and that is described below. If you wish to explore the source code, generate the documentation and run tests on your local machine, it is better to take the latter approach, and that is described in the next section.

### Requirements
* Python 3.10+
* numpy
* scipy
* sympy

### Install from PyPI
Create a separate directory and create a virtual environment. Activate the virtual environment and install required packages. First, choose the directory where you wish to create your project and change into that directory. On *nix systems, do the following:
```bash
$ mkdir rcd_tutorial
$ cd rcd_tutorial
$ python -m venv .venv
$ .venv/bin/activate
$ _
```

On Windows, do the following:
```bash
> mkdir rcd_tutorial
> cd rcd_tutorial
> python -m venv .venv
> .venv\Scripts\activate
> (.venv) _
```

Install using `pip`
```bash
$ (.venv) pip install -U rcdesign
$ (.venv) python -c "from rcdesign import __version__;print(__version____)
$ 0.4.13
```

Run the two built-in example problems and study the output.
```bash
$ (.venv) python -m rcdesign
```

## Install from Source on GitHub

Installing source code from GitHub is mainly for those interested in exploring the source code to understand how the code works and possibly remove bugs and/or make improvements.

### Clone the repository
Choose a suitable directory where you wish to clone the source code from github.  Clone the repository using `git`
```bash
$ git clone https://github.com/satish-annigeri/rcdesign.git
```
This creates a new directory named `rcdesign` in the current working directory. Change over to the directory `rcdesign` that is created with the command
```bash
$ cd rcdesign
```
List the directory contents and verify the directory structure.

### Install required packages
Using `uv` for project management simplifies the process a great deal. Therefore install `uv` before starting with the steps below. Note however, that using `uv` is not essential but the required steps are not described here. Since the project uses `pyproject.toml`, installing required packages using `pip` is straight forward.

Install required packages into the virtual environment with `uv`
```bash
$uv sync --group test
```
This will install pytest and pytest-cov required to run the tests.

### Run tests

Run the tests with `pytest`
```bash
$ uv run pytest tests
```
Check code coverage.
```bash
$ uv run pytest --cov=src --cov-report=html tests
```
With `uv`, there is no need to activate and deactivate the virtual environment, but it is there if you want to use it. The virtual environment is named `.venv` and can be activated in the usual way (`.venv\Scripts\activate` on Windows and `source .venv/bin/activate` on GNU/Linux). Remember to deactivate the virtual environment When you are done, with the command `deactivate` at the command prompt in all operating systems.


## Testing
Testing  has been implemented using `pytest` and unit tests have been implemented for the following classes:

1. **ConcreteLSMFlexure** and **Concrete**
2. **RebarMS** and **RebarHYSD**
3. **RebarLayer** and **RebarGroup**
4. **ShearReinforcement** and **Stirrups**
5. **RectBeamSection** and **FlangedBeamSection**
6. **RectColumnSection**

Code coverage through tests using `pytest-cov` at the current time is 100%, excepting the example script and the methods that implement `__repe__()` and `report()`.

Analysis of rectangular and flanged beam sections with and without compression reinforcement, for flexure and shear, has been completed. Several examples have been solved and verified by hand to consider different cases.

Analysis of rectangular column sections for combined axial compression and bending about one axis has been completed. An example has been solved and verified by hand.

## Examples
### Built-in Example
Run the built-in example with the following command.
```bash
$ uv run python -m rcdesign
```

### Examples from `tests` Directory
Run the additional examples in the `tests` directory with the following command from the command prompt:
```bash
$ uv run python -m tests.example01
$ uv run python -m tests.example02
...
$ uv run python -m tests.example09
```

### Your Own Example
Alternately, you can create the following Python script `example.py`, which is in fact the first example in the `__main__.py` file of the `rcdesign` package (the built-in example), and run the script.

```python
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    ShearRebarGroup,
    Stirrups,
)
from rcdesign.is456.section import RectBeamSection

sb = LSMStressBlock("LSM Flexure")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer(fe415, [20, 16, 20], -35)
steel = RebarGroup([t1])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 450, sb, m20, steel, sh_st, 25)
xu = sec.xu(0.0035)RECTANGULAR BEAM SECTION: 230 x 450
```

Run the script and check the output.

```bash
Example 1

RECTANGULAR BEAM SECTION: 230 x 450
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
FLEXURE
=======
Equilibrium NA = 179.94 (k = 0.40) (ec_max = 0.003500)

   fck                             ec_max Type            f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
 20.00                         0.00350000    C            8.93   299.30    31.45
--------------------------------------------------------------------------------

    fy         Bars       xc       Strain Type     f_sc   f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
   415    1-16;2-20   415.00  -0.00457204    T  -360.87         -299.30    70.35
--------------------------------------------------------------------------------
                                                                   0.00   101.81
SHEAR
=====
          Type                 tau_c      Area (mm^2)                   V_uc (kN)
---------------------------------------------------------------------------------
      Concrete                  0.59         95450.00                      56.46
---------------------------------------------------------------------------------
          Type        Variant    f_y             Bars      s_v     A_sv V_us (kN)
---------------------------------------------------------------------------------
      Stirrups       Vertical    415             2-8#    150.0   100.53   100.37
                                                                        ========
                                                                          156.83
CAPACITY
========
Mu = 101.81 kNm
Vu = 156.83 kN

================================================================================

Example 2

RECTANGULAR BEAM SECTION: 230 x 450
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
FLEXURE
=======
Equilibrium NA = 136.21 (k = 0.30) (ec_max = 0.003500)

   fck                             ec_max Type            f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
 20.00                         0.00350000    C            8.93   226.56    18.02
--------------------------------------------------------------------------------

    fy         Bars       xc       Strain Type     f_sc   f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
   415         2-16    35.00   0.00260065    C   347.70   8.93   136.23    13.79
   415         2-16   380.00  -0.00626432    T  -360.87         -145.11    35.38
   415         3-16   415.00  -0.00716367    T  -360.87         -217.67    60.68
--------------------------------------------------------------------------------
                                                                -226.56   109.85
                                                               =================
                                                                   0.00   127.87
SHEAR
=====
          Type                 tau_c      Area (mm^2)                   V_uc (kN)
---------------------------------------------------------------------------------
      Concrete                  0.64         92230.00                      59.21
---------------------------------------------------------------------------------
          Type        Variant    f_y             Bars      s_v     A_sv V_us (kN)
---------------------------------------------------------------------------------
      Stirrups       Vertical    415             2-8#    150.0   100.53    96.98
                                                                        ========
                                                                          156.19
CAPACITY
========
Mu = 127.87 kNm
Vu = 156.19 kN
```
