# `rcdesign`
<img alt="PyPI - License" src="https://img.shields.io/pypi/l/rcdesign"> [![PyPI version shields.io](https://img.shields.io/pypi/v/rcdesign.svg)](https://pypi.python.org/pypi/rcdesign/) [![Documentation Status](https://readthedocs.org/projects/rcdesign/badge/?version=latest)](http://rcdesign.readthedocs.io/?badge=latest) [![PyPI download month](https://img.shields.io/pypi/dm/rcdesign.svg)](https://pypi.python.org/pypi/rcdesign/) 

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
> python -m rcdesign.example
```

If installation is successful, the example problem must run and you should see the output.

## Install from Source on github
To install from github, you can clone the github repository and give it a try. If you are not familiar with the workflow for working with a source repository, you can follow the steps below.

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
When you clone the `rcdesign` repository from github, a new directory named `rcdesign` will be created in the current working directory. Therefore change over to the a suitable directory which will become the parent directory of the clone. Clone the repository using `git`
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

If you are using Windows operating system, the command is
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
You can also use `nox` to run the tests.
```bash
(env) $ nox
```
When you are done using the virtual environment, you can deactivate with the command `deactivate` at the command prompt in all operating systems.


## A Simple Example
Run the built-in example with the following command.
```bash
(env) $ python -m rcdesign.example
```

Alternately, you can create the following Python script `example.py` and run it.
```python
from rcdesign.is456.material.concrete import ConcreteLSMFlexure, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import RectBeamSection


sb = ConcreteLSMFlexure("IS456 LSM")
m20 = Concrete("M20", 20, sb)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer([20, 16, 20], -35)
steel = RebarGroup(fe415, [t1])
sh_st = Stirrups(fe415, 2, 8, 150)

sec = RectBeamSection(230, 450, m20, steel, sh_st, 25)
print(sec)
xu = sec.xu(0.0035)
print(f"xu = {xu:.2f}")
print(sec.report(xu, 0.0035))
```

Run the script:
```bash
$ python example.py
```

In either case, you must see the result output to the screen.
```term
Size: 230 x 450
Tension Steel: Rebar Group Fe 415 in 1 layer
        dc        xc        Bars      Area
    -35.00    415.00   1-16;2-20    829.38
                    ----------------------
                           Total    829.38

xu = 179.94
Rectangular Beam Section 230 x 450  (xu = 179.94)
Concrete: 20, Tension Steel: 415.00
Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm
Flexure Capacity
Concrete in Compression
                                                              C (kN) M (kNm)
                                                              299.30   31.45
                --------                                    ----------------
                    0.00                                      299.30   31.45
Tension Steel
      dc    Bars    Area       x      Strain    f_st          T (kN) M (kNm)
   -35.01-16;2-20  829.38  235.06  4.5720e-03  360.87          299.30   70.35
                --------                                    ----------------
                  829.38                                      299.30   70.35
                                                            ================
                                                                 0.0  101.81
Shear Capacity
Shear reinforcement: Vertical Stirrups 2-8 @ 150 c/c
pst = 0.87%, d = 415.00, tau_c (N/mm^2) = 0.59
Vuc (kN) = 100.37, Vus = 56.46, Vu (kN) = 156.83
```

## Contribute
Contributions are welcome. Contributions can be in a variety of forms:

1. Bug reports
2. Additional features
3. Documentation
4. Additional examples

## Links
- Documentation: [Documentation](https://rcdesign.readthedocs.io/en/latest/)
- PyPI release: 0.2.0
- Github repository: https://github.com/satish-annigeri/rcdesign

## What `rcdesign` can and cannot do

At present `rcdesign` **can do** the following:

1. Analyse reinforced concrete rectangular and flanged sections subjected to bending and shear as per the Limit State Method according to IS&nbsp;456:2000, the Indian standard code of practice for plain and reinforced concrete. This calculates the ultimate strength of the section in bending and shear depending on the materials, section size and main (longitudinal) and shear reinforcement.
2. Model stress strain relationship of 
    1. concrete in flexure as per IS&nbsp;456:2000&nbsp;(38.1), and 2. reinforcement bars with
        - mild steel bars with well defined yield point
        - cold worked deformed bars
3. Model layers of reinforcement bars placed parallel to the edge of the section at a given distance from the compression (or tension edge). Bars can be of different diameters but must be of the same type.
4. Model group of layers of reinforcement bars. All bars in agroup must be of the same type and layers of reinforcement must be placed parallel to the edge of the section.
5. Model shear reinforcement in the form of vertical stirrups, inclined stirrups and bent-up bars.
6. Model rectangular and flanged sections. Sections must be of a given concrete. Main (longitudinal) reinforcement to resist bending must be provided as a single group of reinforcement layers, possibly with one or more layers in the compression zone and one or more layers in the tension zone. However, note that the position of the neutral axis is dependent on the sectiion size and the amount and location of main reinforcement. Only after an analysis of the section will it be clear whether a given layer of reinforcement in the group lies in the compression or tension zone.

At present, `rcdesign` **cannot do** the following:
1. Does not analyse sections subjected to axial compression (with or without bending about an axis parallel to one of the edges). This is on the TO&nbsp;DO list.
2. Does not design sections, either for bending, shear and torsion or for axial compression with or without bending about one or both axes.
3. Does not verify whether the section meets the detailing requirements of IS&nbsp;456:2000&nbsp;(26).
4. Does not analyse or design sections as per Working Stress Method of IS&nbsp;456:2000&nbsp;(Annexure&nbsp;N).
5. Does not design reinforced concrete elements such as beams and columns. At present, the scope of the package is restricted to analysis and design of sections of beams and columns. This is a distant goal, but no promises.

Some or all of the above features will be gradually included. Contributions in accomplishing these are welcome.

## Current Status

The package is in early development and has undergone testing of the current code base for coverage. Limited examples have been solved and verified by hand.

### Classes
The following classes have been implemented:

1. An abstract base class **StressBlock** to represent a stress block. A derived class **ConcreteLSMFlexure** to represent the stress block for concrete in compression under limit state of flexure, derived from the abstract StressBlock class.
3. A class **Concrete** to represent concrete which consists of a ConcreteLSMFlexure.
4. An abstract class **Rebar** to represent reinforcement bars. Two derived classes **RebarMS** and **RebarHYSD** to represent mild steel bars and high yield strength deformed bars, respectively.
5. A class **RebarLayer** to represent a single layer of reinforcement bars, defined as a list of bar diameters and the distance of the centre of the bars from the nearest edge. A class **RebarGroup** to represnt a list of layers of reinforcement bars.
6. An abstract class **ShearReinforcement** to represent shear reinforcement. Two derived classes **Stirrups** and **BentupBars** to represent vertical/inclined stirrups and bent up bars, respectively.
7. An abstract class **Section** to represnt a cross section. Two derived classes **RectBeamSection** and **FlangedBeamSection** to represnt rectangular and flanged sections subejcted to flexure and shear.

### Methods
Following funcationality has been implemented for the different classes:

1. **ConcreteLSMFlexure**: Calculation of design stress, stress at a specified distance $x$ from neutral axis, area of stress block between two locations $x_1$ and $x_2$ from neutral axis and moment of stress block between the two locations with respect to depth $x_u$ of the neutral axis.
2. **RebarMS** and **RebarHYSD**: Stress for a specified value of strain and design stress.
3. **RebarLayer**: Area of bars in a layer.
4. **RebarGroup**: Calculation of the sum of the following values aggregated after calculating the values individually for each layer:
    * Area of reinforcing bars in the group,
    * Force in reinforcing bars in the group, in tension and in compression,
    * Moment of force in reinforcing bars in the group about the neutral axis, in tension and in compression
5. **RectBeamSection** and **FlangedBeamSection**: Calculation of:
    * Total compression force and the corresponding moment about the neutral axis for a specified neutral axis location $x_u$, considering concrete in compression and compression reinforcement bars, if present,
    * Total tension force and the corresponding moment about the neutral axis due to a group of tension reinforcement bars,
    * Position of the neutral axis $x_u$, calculated iteratively to satisfy equilibrium,
    * Shear force capacity of a section for a given shear reinforcement in the form of vertical or inclined stirrups,
    * Spacing of vertical or inclined stirrups for a given design shear force

### Testing
Testing  has been implemented using `pytest` and unit tests have been implemented for the following classes:

1. **ConcreteLSMFlexure** and **Concrete**
2. **RebarMS** and **RebarHYSD**
3. **RebarLayer** and **RebarGroup**
4. **ShearReinforcement** and **Stirrups**
5. **RectBeamSection** and **FlangedBeamSection**

Code coverage through tests using `pytest-cov` at the current time is 100%. Analysis of rectangular and flanged beam sections with and without compression reinforcement, for flexure and shear, has been completed. Several examples have been solved and verified by hand to consider different cases.

Automated testing can be donw using. Verify that `nox` is installed with the command
```bash
(env) $ nox --version
2021.6.12
```

### Documentation
[Documentation is available here](https://rcdesign.readthedocs.io/en/latest/). Any advise or help on documentation is welcome.

## Future Plans

Immediate plans include the analysis and design at the *section* level:

1. Design sections subjected to bending, shear and torsion.
1. Analysis of rectangular *sections* subjected to axial compression and bending about one axis.
2. Write user and API documentation using Sphinx.
2. Design of rectangular and flanged *sections* subjected to bending, shear and torsion.
3. Design of column *sections*.
4. Detailing of *sections* subjected to bending, shear and torsion.
5. Implementing a stress block to represent *working stress method*.

Long term plans include:

1. Design and detailing of reinforced concrete elements such as beams, columns, slabs, footings, retaining walls etc.
2. Calculation of deflections of elements.
3. Design and detailing of reinforced concrete structures, including detailing of joints (very far into the future, if at all).

## References
1. IS 456:2000 Indian Standard Code of Practice for Plain and Reinforced Concrete (Fourth Revision), Bureau of Indian Standards, New Delhi, 2000.
2. SP:24 (S&T)-1983 Explanatory Handbook on Indian Standard Code of Practice for Plain and Reinforced Concrete (IS 456:1978), Bureau of Indian Standards, New Delhi, 1984.
3. SP 16:1980 Design Aids for Reinforced Concrete to IS:456-1978, Bureau of Indian Standards, New Delhi, 1980.