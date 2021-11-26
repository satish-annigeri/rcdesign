# Tutorial
## Install `rcdesign`
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

## Singly reinforced rectangular section
Consider a rectangular reinforced concrete section with the following details:
1. Size: 230x450 mm overall with 25mm clear cover
2. Concrete: M20
3. Steel: Fe415
4. Main reinforcement: 3-16# of Fe415 with centre of the bars at a distance of 35mm from tension edge of the section
4. Shear reinforcement: 2-8# @ 150mm c/c (2 legged 8mm dia. vertical stirrups made of Fe415)

Let us determine the Limit State capacity of the section in bending and shear.

Create a Python script named `singly01.py` and type the following code in it.

```python
# File: singly01.py
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups, ShearRebarGroup
from rcdesign.is456.section import RectBeamSection

# Create the materials
# Concrete
csb = ConcreteStressBlock('IS456 LSM')
m20 = Concrete('M20', 20, csb)
# Reinforcement
fe415 = RebarHYSD('Fe 415', 415)
layer = RebarLayer([16, 16, 16], -35)
main_steel = RebarGroup(fe415, [layer])
shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])
# Section
rsec = RectBeamSection(230, 450, m20, main_steel, shear_steel, 25)

# Calculate depth of neutral axis
xu = rsec.xu(0.0035)
# Report limit state capacity
print(rsec.report(xu, 0.0035))
```
Run the script from the command line:
```bash
$ python singly01.py
```

The output of the script must be
```bash
RECTANGULAR BEAM SECTION: 230 x 450
FLEXURE
Equilibrium NA = 130.87 (ec,max = 0.003500)
Concrete: Stress Block IS456 LSM - M20: fck = 20.00 N/mm^2, fd = 8.93 N/mm^2
            dc    xc        Bars      Area  Stress      x NA      Strain        fs        fc     Force    Moment
Concrete                                         C    130.87  3.5000e-03                8.93    217.67     16.64
   Rebar   -35   415        3-16    603.19       T    284.13  7.5990e-03    360.87              217.67     61.85
                                                                                            --------------------
                                                                                                  0.00     78.48
SHEAR
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 78.48 kNm
Vu = 150.44 kN
```

## Doubly reinforced rectangular section
Consider a rectangular reinforced concrete section with the following details:
1. Size: 230x450 mm overall with 25mm clear cover
2. Concrete: M20
3. Steel: Fe415
4. Main reinforcement:
    1. 2-16# of Fe415 with centre of the bars at a distance of 35mm from compression edge of the section
    2. 3-16# of Fe415 with centre of the bars at a distance of 35mm from tension edge of the section
4. Shear reinforcement: 2-8# @ 150mm c/c (2 legged 8mm dia. vertical stirrups made of Fe415)

Let us determine the Limit State capacity of the section in bending and shear.

Create a Python script named `doubly02.py` and type the following code in it.

```python
# File: doubly02.py
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups, ShearRebarGroup
from rcdesign.is456.section import RectBeamSection

# Doubly reinforced rectangular section
# Create the materials
# Concrete
csb = ConcreteStressBlock('IS456 LSM')
m20 = Concrete('M20', 20, csb)
# Reinforcement
fe415 = RebarHYSD('Fe 415', 415)
layer1 = RebarLayer([16, 16], 35)
layer2 = RebarLayer([16, 16, 16], -35)
main_steel = RebarGroup(fe415, [layer1, layer2])
shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])
# Section
rsec = RectBeamSection(230, 450, m20, main_steel, shear_steel, 25)

# Calculate depth of neutral axis
xu = rsec.xu(0.0035)
# Report limit state capacity
print(rsec.report(xu, 0.0035))
```
Run the script from the command line:
```bash
$ python doubly02.py
```

The output of the program must be:
```bash
RECTANGULAR BEAM SECTION: 230 x 450
FLEXURE
Equilibrium NA = 61.57 (ec,max = 0.003500)
Concrete: Stress Block IS456 LSM - M20: fck = 20.00 N/mm^2, fd = 8.93 N/mm^2
            dc    xc        Bars      Area  Stress      x NA      Strain        fs        fc     Force    Moment
Concrete                                         C     61.57  3.5000e-03                8.93    102.41      3.68
   Rebar    35    35        2-16    402.12       C     26.57  1.5103e-03    295.04      8.40    115.26      3.06
   Rebar   -35   415        3-16    603.19       T    353.43  2.0092e-02    360.87              217.67     76.93
                                                                                            --------------------
                                                                                                  0.00     83.68
SHEAR
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 83.68 kNm
Vu = 150.44 kN
```

## Flanged Beam

1. Web size: 230x450 mm overall with 25mm clear cover
2. Flange size: Width=900 mm and depth = 150 mm
2. Concrete: M20
3. Steel: Fe415
4. Main reinforcement: 3-16# of Fe415 with centre of the bars at a distance of 35mm from tension edge of the section
4. Shear reinforcement: 2-8# @ 150mm c/c (2 legged 8mm dia. vertical stirrups made of Fe415)

Let us determine the Limit State capacity of the section in bending and shear.

Create a Python script named `flanged03.py` and type the following code in it.

```python
FLANGED BEAM SECTION - Web: 230 x 450, Flange: 900 x 150
FLEXURE
Equilibrium NA = 52.26 (ec,max = 0.003500)
Concrete: Stress Block IS456 LSM - M20: fck = 20.00 N/mm^2, fd = 8.93 N/mm^2
            dc    xc        Bars      Area  Stress      x NA      Strain        fs        fc     Force    Moment
Concrete                                         C     52.26  3.5000e-03                8.93    340.11     10.38
   Rebar   -35   415        3-20    942.48       T    362.74  2.4296e-02    360.87              340.11    123.37
                                                                                            --------------------
                                                                                                  0.00    133.75
SHEAR
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 133.75 kNm
Vu = 159.52 kN
```