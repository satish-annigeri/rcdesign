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
> python -m rcdesign
```

If installation is successful, the example problems must run and you should see the output.

## Install from Source on github
To install from github, clone the github repository and give it a try. If you are not familiar with the workflow for working with a source repository, follow these steps.

### Preliminary checks
Check the version of Python you are using. You will require version 3.7 or later. To print the version of Python, use the command
```bash
$ python -V
Python 3.9.7
```
On a *nix system, you may have to type
```bash
$ python3 -V
Python 3.9.7
```

### Clone the repository
When you clone the `rcdesign` repository from github, a new directory named `rcdesign` will be created in the current working directory. Therefore change over to a suitable directory within which to clone the repository. Clone the repository using `git`
```bash
$ git clone https://github.com/satish-annigeri/rcdesign.git
```

Change over to the directory `rcdesign` that is created with the command
```bash
$ cd rcdesign
```
List the directory contents and verify the directory structure.

### Create a virtual environment
Create a virtual environment inside the `rcdesign` directory with the following command
```bash
$ python -m venv env
```
Activate the virtual environment with the command
```bash
$ source env/bin/activate
(env) $_
```

For Windows operating system, the command is
```bash
> env\Scripts\activate
(env) >_
```
Update `pip` with the command
```bash
(env) $ python -m pip install -U pip
```
### Install required packages
Install required packages into the virtual environment with `pip`
```bash
(env) $ pip install -r requirements.txt
```
### Run tests
Install additional packages required to run tests.
```bash
(env) pip install pytest pytest-cov nox
```
Run the tests with `pytest`
```bash
(env) $ pytest tests
```
Check code coverage.
```bash
(env) $ pytest --cov=rcdesign tests/
```
You can also use `nox` to run the tests. Install `nox` using `pip`, if necessary.
```bash
(env) $ pip install nox
(env) $ nox
```
When you are done using the virtual environment, you can deactivate it with the command `deactivate` at the command prompt in all operating systems.

## Examples
### Built-in Example
Run the built-in example with the following command.
```bash
(env) $ python -m rcdesign
```

### Examples from `tests` Directory
Run the examples in the `tests` directory with the following command from the command prompt:
```bash
(env) $ python -m tests.example01
(env) $ python -m tests.example02
...
(env) $ python -m tests.example09
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

Check the output.

```bash
Example 1

RECTANGULAR BEAM SECTION: 230 x 450
FLEXURE
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
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 101.81 kNm
Vu = 156.83 kN

================================================================================

Example 2

RECTANGULAR BEAM SECTION: 230 x 450
FLEXURE
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
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 127.87 kNm
Vu = 156.19 kN
```

## Contribute
Contributions are welcome. Contributions can be in a variety of forms:

1. Bug reports
2. Additional features
3. Documentation
4. Additional examples

## Links
- Documentation: [Documentation](https://rcdesign.readthedocs.io/en/latest/)
- PyPI release: [0.4.0](https://pypi.org/project/rcdesign/)
- Github repository: https://github.com/satish-annigeri/rcdesign

## What `rcdesign` can and cannot do

At present `rcdesign` **can do** the following:

1. Analyse reinforced concrete rectangular and flanged sections subjected to bending and shear as per the Limit State Method according to IS&nbsp;456:2000, the Indian standard code of practice for plain and reinforced concrete. This calculates the ultimate strength of the section in bending and shear depending on the materials, section size and main (longitudinal) and shear reinforcement.
2. Analyses reinforced concrete rectangular sections subjected to axial compression and bending about one axis parallel to the first (usually the short) edge, as per limit state method of IS&nbsp;456:2000.
3. Represent stress strain relationship for: 
    1. concrete in flexure as per IS&nbsp;456:2000&nbsp;(38.1),
    2. concrete under axial compression and flexure as per IS&nbsp;456:2000&nbsp;(39.1),
    2. reinforcement bars:
        1. mild steel bars with well defined yield point
        2. cold worked deformed bars
4. Represent layers of reinforcement bars placed parallel to the edge of the section at a given distance from the compression (or tension edge). Bars can be of different diameters but must be of the same type.
5. Represent group of layers of reinforcement bars. All bars in agroup must be of the same type and layers of reinforcement must be placed parallel to the edge of the section.
6. Represent group of shear reinforcement in the form of vertical stirrups, inclined stirrups and bent-up bars. 

Rectangular and flanged sections must be of a given grade of concrete. Main (longitudinal) reinforcement to resist bending must be provided as a single group of reinforcement layers, possibly with one or more layers in the compression zone in addition to one or more layers in the tension zone. However, since the position of the neutral axis is dependent on the section size and the amount and location of main reinforcement, whether a layer of reinforcement lies in the tension zone or the compression zone will be known after an analysis of the section.

At present, `rcdesign` **cannot do** the following:
1. Cannot design sections, either for bending, shear and torsion or for axial compression with or without bending about one or both axes.
3. Cannot verify whether the section meets the detailing requirements of IS&nbsp;456:2000&nbsp;(26).
4. Cannot analyse or design sections as per Working Stress Method of IS&nbsp;456:2000&nbsp;(Annexure&nbsp;N).
5. Cannot design reinforced concrete elements such as beams and columns. At present, the scope of the package is restricted to analysis and design of sections of beams and columns. This is a distant goal, but no promises.

Some or all of the above features will be gradually included. Contributions in accomplishing these are welcome.

## Current Status

The package is in early development and may undergo backward incompatible changes. It has undergone testing of the current code base. Limited examples have been solved and verified by hand. Test coverage is currently 100% (excepting the example script).

### Classes
The following classes have been implemented:

1. A class **LSMStressBlock** to represent the stress block for concrete in compression under limit state of flexure, as well as limit state of combined axial compression and flexure as per IS&nbsp;456:2000.
2. A class **Concrete** to represent concrete.
3. An abstract class **Rebar** to represent reinforcement bars. Two derived classes **RebarMS** and **RebarHYSD** to represent mild steel bars and high yield strength deformed bars, respectively.
4. A class **RebarLayer** to represent a single layer of reinforcement bars, defined as a list of bar diameters and the distance of the centre of the bars from the nearest edge. A class **RebarGroup** to represnt a list of layers of reinforcement bars.
5. An abstract class **ShearReinforcement** to represent shear reinforcement. Two derived classes **Stirrups** and **BentupBars** to represent vertical/inclined stirrups and bent up bars, respectively.
6. A class **ShearRebarGroup** to represent a group of shear reinforcement bars.
7. A class **RectBeamSection** to represnt a reinforced concrete rectangular beam section. A derived class **FlangedBeamSection** to represnt flanged sections subejcted to flexure and shear, derived from **RectBeamSection**.
8. A class *RectColumnSection** to represent a reinforced concrete rectangular coulmn section subjected to combined axial compression and bending about one axis.

### Methods
Following funcationality has been implemented for the different classes:

1. **LSMStressBlock**: Calculation of the following:
    1. strain distribution,
    2. stress for a given strain,
    3. stress at a specified distance $x$ from neutral axis,
    4. area of stress distribution between two locations $x_1$ and $x_2$ from neutral axis, and
    5. moment of stress block between the two locations with respect to depth $x_u$ of the neutral axis.

    These are implemented for both the following cases:

    1. Flexure
    2. Combined axial compression and bending about one axis.
2. **Concrete**: Calculation of design stress $f_d$, shear stress $\tau_c$ and maximum shear stress $\tau_{c,max}$.
3. **RebarMS** and **RebarHYSD**: Stress for a specified value of strain and design stress.
4. **RebarLayer**: Area of bars in a layer.
5. **RebarGroup**: Calculation of the sum of the following values aggregated after calculating the values individually for each layer:
    * Area of reinforcing bars in the group,
    * Force in reinforcing bars in the group, in tension and in compression,
    * Moment of force in reinforcing bars in the group about the neutral axis, in tension and in compression
6. **RectBeamSection** and **FlangedBeamSection**: Calculation of:
    * Total compression force and the corresponding moment about the neutral axis for a specified neutral axis location $x_u$, considering concrete in compression and compression reinforcement bars, if present,
    * Total tension force and the corresponding moment about the neutral axis due to a group of tension reinforcement bars,
    * Position of the neutral axis $x_u$, calculated iteratively to satisfy equilibrium,
    * Shear force capacity of a section for a given shear reinforcement in the form of vertical or inclined stirrups,
    * Spacing of vertical or inclined stirrups for a given design shear force
7. **RectColumnSection**: Calculation of:
    * Total axial compression force and bending moment about the neutral axis for a given position of the neutral axis.

### Testing
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

Automated testing can be done using. Check to ensure that `nox` is installed using the command
```bash
(env) $ nox --version
2021.6.12
```
If required, install `nox` with the command:
```bash
(env) $pip install nox
```

### Documentation
[Documentation is available here](https://rcdesign.readthedocs.io/en/latest/). Any advise or help on documentation is welcome.

## Future Plans

Immediate plans include the design of *sections*:

1. Design of rectangular and flanged sections subjected to bending, shear and torsion.
2. Write user and API documentation using Sphinx.
3. Design of rectangular column *sections*.
4. Detailing of rectangular beam *sections* subjected to bending, shear and torsion.
5. Design of rectangular column *sections* subjected to combined axial compression and bending.
5. Implementing a stress block to represent *working stress method*.

Long term plans include:

1. Design and detailing of reinforced concrete elements such as beams, columns, slabs, footings, retaining walls etc.
2. Calculation of deflections of elements.
3. Design and detailing of reinforced concrete structures, including detailing of joints (very far into the future, if at all).

## References
1. IS 456:2000 Indian Standard Code of Practice for Plain and Reinforced Concrete (Fourth Revision), Bureau of Indian Standards, New Delhi, 2000.
2. SP:24 (S&T)-1983 Explanatory Handbook on Indian Standard Code of Practice for Plain and Reinforced Concrete (IS 456:1978), Bureau of Indian Standards, New Delhi, 1984.
3. SP 16:1980 Design Aids for Reinforced Concrete to IS:456-1978, Bureau of Indian Standards, New Delhi, 1980.