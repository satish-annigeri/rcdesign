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
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import RectBeamSection

# Create the materials
# Concrete
csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
m20 = Concrete('M20', 20, csb)
# Reinforcement
fe415 = RebarHYSD('Fe 415', 415)
layer = RebarLayer([16, 16, 16], -35)
main_steel = RebarGroup(fe415, [layer])
shear_steel = Stirrups(fe415, 2, 8, 150)
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
Rectangular Beam Section 230 x 450  (xu = 130.87)
Concrete: 20, Tension Steel: 415.00
Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm
Flexure Capacity
Concrete in Compression
                                                              C (kN) M (kNm)
                                                              217.67   16.64
                --------                                    ----------------
                    0.00                                      217.67   16.64
Tension Steel
      dc    Bars    Area       x      Strain    f_st          T (kN) M (kNm)
   -35.0    3-16  603.19  284.13  7.5990e-03  360.87          217.67   61.85
                --------                                    ----------------
                  603.19                                      217.67   61.85
                                                            ================
                                                                 0.0   78.48
Shear Capacity
Shear reinforcement: Vertical Stirrups 2-8 @ 150 c/c
pst = 0.63%, d = 415.00, tau_c (N/mm^2) = 0.52
Vuc (kN) = 100.37, Vus = 50.07, Vu (kN) = 150.44
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
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import RectBeamSection

# Doubly reinforced rectangular section
# Create the materials
# Concrete
csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
m20 = Concrete('M20', 20, csb)
# Reinforcement
fe415 = RebarHYSD('Fe 415', 415)
layer1 = RebarLayer([16, 16], 35)
layer2 = RebarLayer([16, 16, 16], -35)
main_steel = RebarGroup(fe415, [layer1, layer2])
shear_steel = Stirrups(fe415, 2, 8, 150)
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
Rectangular Beam Section 230 x 450  (xu = 61.57)
Concrete: 20, Tension Steel: 415.00, Compression Steel: 415.00
Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm
Flexure Capacity
Concrete in Compression
                                                              C (kN) M (kNm)
                                                              102.41    3.68
Compression Steel
      dc    Bars    Area       x      Strain    f_sc    f_cc  C (kN) M (kNm)
    35.0    2-16  402.12   26.57  1.5103e-03  295.04    8.40  115.26    3.06
                --------                                    ----------------
                  402.12                                      217.67    6.74
Tension Steel
      dc    Bars    Area       x      Strain    f_st          T (kN) M (kNm)
   -35.0    3-16  603.19  353.43  2.0092e-02  360.87          217.67   76.93
                --------                                    ----------------
                  603.19                                      217.67   76.93
                                                            ================
                                                                 0.0   83.68
Shear Capacity
Shear reinforcement: Vertical Stirrups 2-8 @ 150 c/c
pst = 0.63%, d = 415.00, tau_c (N/mm^2) = 0.52
Vuc (kN) = 100.37, Vus = 50.07, Vu (kN) = 150.44
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
# File: flanged03.py
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import FlangedBeamSection

# Singly reinforced flanged section
# Create the materials
# Concrete
csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
m20 = Concrete('M20', 20, csb)
# Reinforcement
fe415 = RebarHYSD('Fe 415', 415)
layer = RebarLayer([20, 20, 20], -35)
main_steel = RebarGroup(fe415, [layer])
shear_steel = Stirrups(fe415, 2, 8, 150)
# Section
rsec = FlangedBeamSection(230, 450, 900, 150, m20, main_steel, shear_steel, 25)

# Calculate depth of neutral axis
xu = rsec.xu(0.0035)
# Report limit state capacity
print(rsec.report(xu, 0.0035))
```
Run the script from the command line:
```bash
$ python flanged03.py
```

The output of the program must be:
```bash
Flanged Beam Section 230 x 450, bf = 900, Df = 150, (xu = 52.26)
Concrete: 20, Tension Steel: 415, Compression Steel: 415
Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm
Flexure Capacity
                         Cw (kN) Mw (kN) Cf (kN) Mf (kN)  C (kN) M (kNm)
------------------------------------------------------------------------
                           86.92    2.65  253.19    7.73  340.11   10.38
                                                        ----------------
                                                          340.11   10.38
Tension Reinforcement
  dc    Bars    Area       x      Strain    f_st          C (kN) M (kNm)
------------------------------------------------------------------------
 -35    3-20  942.48  362.74  2.4296e-02  360.87          340.11  123.37
                                                        ----------------
                                                          340.11  123.37
                                                        ================
                                                            0.00  133.75
```