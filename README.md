# `rcdesign` - A Python package for analysis and design of reinforced concrete sections as per IS 456:2000

This is a Python package for analysis and design of reinforced concrete sections as per IS 456:2000, the Indian Standard code of practice for plain and reinforced concrete. All units are Netwon and millimeter.

## Installation
`rcdesign` is still under development and can be installed by cloning this repository with `git`

`git clone https://github.com/satish-annigeri/rcdesign.git`

## Quickstart
After cloning the `rcdesign` repository from github, change into the newly created `rcdesign` directory. The directory will have the following structure (as of 2021-09-06):

    rcdesign/
    ├── LICENSE.md
    ├── main.py
    ├── poetry.lock
    ├── pyproject.toml
    ├── rcdesign
    │   ├── __init__.py
    │   ├── is456
    │   │   ├── __init__.py
    │   │   ├── material
    │   │   │   ├── concrete.py
    │   │   │   ├── __init__.py
    │   │   │   └── rebar.py
    │   │   └── section.py
    │   └── utils.py
    ├── README.md
    └── tests
        ├── __init__.py
        ├── test_concrete.py
        ├── test_rebargroup.py
        ├── test_rebarlayer.py
        ├── test_rebar.py
        ├── test_section.py
        ├── test_shear_rebar.py
        └── test_utils.py

Install a virtual environment in your preferred way and install the necessary packages. If you are using `poetry`, there is the `pyproject.toml` file and if you are using `pip`, there is the `requirements.txt` file that can be used. With poetry, do

`poetry install`

and with `pip` do

`pip install -r requirements.txt`

With the required packages installed, you can run the `main.py` script in the root directory of the repository with

`python main.py`

and you must see the resuls output to the screen.

    Analysis of Reinforced Concrete Sections v0.1.0

    Size: 230 x 450
    Tension Steel: Rebar Group Fe 415 in 2 layers
        Dia: [16, 16, 16] at 35. Area: 603.19
        Dia: [16, 16] at 70. Area: 402.12
        Total Area: 1005.31 centroid at 49.00 from the edge
    Compression Steel: Rebar Group Fe 415 in 1 layer
        Dia: [16, 16] at 35. Area: 402.12
        Total Area: 402.12 centroid at 35.00 from the edge

    Analysis of section for xu = 150
    Compression (C):     386.59 kN
        Tension (T):     362.79 kN
              C - T:      23.81 kN

    Location of neutral axis for equilibrium
    Neutral axis lies between 120.00 and 155.00 from compression edge
    Depth of neutral axis: 136.21

    Rectangular Beam Section 230x450 (xu = 136.21)
    Units: Distance in mm, Area in mm^2, Force in kN, Moment in kNm
    FLEXURE CAPACITY
    ... (lines omitted)
    SHEAR CAPACITY
    Shear reinforcement: Vertical Stirrups 2-8 @ 150 c/c
    Ultimate shear capacity (kN): 156.19

    Flanged Section
    xu = 50.17 Mu = 137.91


## Objective

The objective is to devlop a package to represent materials, stress blocks, rebars, sections, and other components essential to analyse and design reinforced concrete sections. It is initally planned to carry out analysis of sections before taking up design of sections as per the limit state method of IS 456:2000.

Object oriented programming is particularly well suited to represent problems of this type as inheritance and composition are natural to the representation of structures, their components, and materials as well as their behaviours. Further, speed of execution is not a primary concern, as much as it is in the analysis of structures.

In the beginning, analysis of beam sections - rectangular and flanged, will be taken up to compute capacity of the sections in flexure and shear. Analysis of rectangular column sections will be taken up subsequently. Design of sections will be taken up subsequently.

The package will consist of a classes hierarchy to implement analysis, design and detailing at the *section* level.

## Current Status

The package is in early development and has undergone limited testing. No documentation is available at the current time.

### Classes
The following classes have been implemented:

1. An abstract base class **StressBlock** to represent a stress block. A derived class **ConcreteStressBlock** to represent the stress block for concrete in compression under limit state of flexure, derived from the abstract StressBlock class.
3. A class **Concrete** to represent concrete which consists of a ConcreteStressBlock.
4. An abstract class **Rebar** to represent reinforcement bars. Two derived classes **RebarMS** and **RebarHYSD** to represent mild steel bars and high yield strength deformed bars, respectively.
5. A class **RebarLayer** to represent a single layer of reinforcement bars, defined as a list of bar diameters and the distance of the centre of the bars from the nearest edge. A class **RebarGroup** to represnt a list of layers of reinforcement bars.
6. An abstract class **ShearReinforcement** to represent shear reinforcement. Two derived classes **Stirrups** and **BentupBars** to represent vertical/inclined stirrups and bent up bars, respectively.
7. An abstract class **Section** to represnt a cross section. Two derived classes **RectBeamSection** and **FlangedBeamSection** to represnt rectangular and flanged sections subejcted to flexure and shear.

### Methods
Following funcationality has been implemented for the different classes:

1. **ConcreteStressBlock**: Calculation of design stress, stress at a specified distance $x$ from neutral axis, area of stress block between two locations $x_1$ and $x_2$ from neutral axis and moment of stress block between the two locations with respect to depth $x_u$ of the neutral axis.
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
Testing  has been implemented using pytest and unit tests have been implemented for the following classes:

1. **ConcreteStressBlock** and **Concrete**
2. **RebarMS** and **RebarHYSD**
3. **RebarLayer** and **RebarGroup**
4. **ShearReinforcement** and **Stirrups**
5. **RectBeamSection** and **FlangedBeamSection**

Code coverage through tests using `pytest-cov` is 100%. Analysis of rectangular and flanged beam sections with and without compression reinforcement, for flexure and shear, has been completed. More examples will be verified to consider different cases.

### Documentation
Documentation is presently not available, but is the current ongoing task.

## Future Plans

Immediate plans include the analysis and design at the *section* level:

1. Analysis of rectangular *sections* subjected to axial compression and bending about one axis.
2. Design of rectangular and flanged *sections* subjected to bending, shear and torsion.
3. Design of column *sections*.
4. Detailing of *sections* subjected to bending, shear and torsion.
5. Implementing a stress block to represent working stress method.

Long term plans include:

1. Design and detailing of reinforced concrete elements such as beams, columns, slabs, footings, retaining walls etc.
2. Calculation of deflections of elements.
3. Design and detailing of reinforced concrete structures, including detailing of joints (very far into the future, if at all).

## References
1. IS 456:2000 Indian Standard Code of Practice for Plain and Reinforced Concrete (Fourth Revision), Bureau of Indian Standards, New Delhi, 2000.
2. SP:24 Explanatory Handbook on Indian Standard Code of Practice for Plain and Reinforced Concrete (IS 456:1978), Bureau of Indian Standards, New Delhi, 1984.