# Tutorial
## Install `rcdesign`
Install `rcdesign` from PyPI using `pip` as explained in [Installation](installation.md). Verify that installation is successful, by running the example problem:
```bash
(env) $ python -m rcdesign
```

## Singly reinforced rectangular section
Consider a rectangular reinforced concrete section with the following details:
1. Size: 230x450 mm overall with 25mm clear cover
2. Concrete: M20
3. Steel: Fe415
4. Main reinforcement: Fe415 reinforcement bars 2-16# + 1-20# with centre of the bars at a distance of 35mm from tension edge of the section
4. Shear reinforcement: 2-8# @ 150mm c/c (2 legged 8mm dia. vertical stirrups made of Fe415)

Let us determine the Limit State capacity of the section in bending and shear.

Create a Python script named `singly01.py` and type the following code in it.

```python
# File: example01.py

from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection

sb = LSMStressBlock("LSM Flexure")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer(fe415, [20, 16, 20], -35)
steel = RebarGroup([t1])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 450, sb, m20, steel, sh_st, 25)
xu = sec.xu(0.0035)
print(f"xu = {xu:.2f}")
print(sec.report(xu, 0.0035))
```
Run the script from the command line:
```bash
$ python singly01.py
```

The output of the script must be
```bash
xu = 179.94
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

Create a Python script named `example02.py` and type the following code in it.

```python
# File: example02.py

from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection

sb = LSMStressBlock("IS456 LSM")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer(fe415, [16, 16], 35)
t2 = RebarLayer(fe415, [16, 16, 16], -35)
steel = RebarGroup([t1, t2])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 450, sb, m20, steel, sh_st, 25)
xu = sec.xu(0.0035)
print(sec.report(xu, 0.0035))
```

Run the script from the command line:
```bash
(env) $ python example02.py
RECTANGULAR BEAM SECTION: 230 x 450
FLEXURE
Equilibrium NA = 61.57 (k = 0.14) (ec_max = 0.003500)
   fck                             ec_max Type            f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
 20.00                         0.00350000    C            8.93   102.41     3.68
--------------------------------------------------------------------------------

    fy         Bars       xc       Strain Type     f_sc   f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
   415         2-16    35.00   0.00151034    C   295.04   8.40   115.26     3.06
   415         3-16   415.00  -0.02009170    T  -360.87         -217.67    76.93
--------------------------------------------------------------------------------
                                                                -102.41    79.99
                                                               =================
                                                                   0.00    83.68
SHEAR
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 83.68 kNm
Vu = 150.44 kN
```

## Flanged Beam

1. Web size: 300x475 mm overall with 25mm clear cover
2. Flange size: Width=800 mm and depth = 150 mm
2. Concrete: M25
3. Steel: Fe415
4. Main reinforcement: 2-18# of Fe415 with centre of the bars at a distance of 70&nbsp;mm from tension edge of the section and 3-20# of Fe415 with centre of the bars at a distance of 35&nbsp;mm from tension edge of the section
4. Shear reinforcement: 2-8# @ 150mm c/c (2 legged 8mm dia. vertical stirrups made of Fe415)

Let us determine the Limit State capacity of the section in bending and shear.

Create a Python script named `example03.py` and type the following code in it.

```python
# File: example03.py

from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import FlangedBeamSection

sb = LSMStressBlock("IS456 LSM")
m25 = Concrete("M25", 25)
fe415 = RebarHYSD("Fe 415", 415)
t1 = RebarLayer(fe415, [20, 20, 20], -35)
t2 = RebarLayer(fe415, [18, 18], -70)
main_steel = RebarGroup([t1, t2])
shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])
tsec = FlangedBeamSection(300, 475, 800, 150, sb, m25, main_steel, shear_steel, 25)
xu = tsec.xu(0.0035)
print(tsec.report(xu, 0.0035))
```

Run the example
```bash
(env) $ python example03.py
FLANGED BEAM SECTION - Web: 300 x 475, Flange: 800 x 150
FLEXURE
Equilibrium NA = 72.43 (ec_max = 0.003500)
Concrete: fck = 25.00 N/mm^2, fd = 11.17 N/mm^2
   fck    Breadth      Depth       ec_min        ec_max   Type   C (kN)  M (kNm)
--------------------------------------------------------------------------------
    25     300.00     475.00   0.00000000    0.00350000      C   196.41     8.31
    25     800.00     150.00                 0.00350000      C   327.36    13.85
--------------------------------------------------------------------------------
                                                                 523.77    22.16

    fy         Bars       xc       Strain Type     f_sc   f_cc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
   415         2-18   405.00  -0.01607150    T  -360.87         -183.66    61.08
   415         3-20   440.00  -0.01776287    T  -360.87         -340.11   125.02
--------------------------------------------------------------------------------
                                                                -523.77   186.10
                                                               =================
                                                                   0.00   208.25
SHEAR
Vertical Stirrups: Fe 415 2-8 @ 150 c/c (Asv = 100.53)

CAPACITY
Mu = 208.25 kNm
Vu = 189.58 kN
```

## Rectangular Column
1. Rectangular column of size: 230x450&nbsp;mm
2. Concrete: M20
3. Steel: Fe415
4. Longitudinal reinforcement: Fe415 in three layers:
      1. 3-16# at 50&nbsp;mm from highly compressed edge
      2. 2-16# at 225&nbsp;mm from highly compressed edge
      3. 3-16# at 400&nbsp;mm from highly compressed edge (or 50&nbsp;mm from the least compressed edge)
5. Location of neutral axis: At 900&nbsp;mm from highly compressed edge ($x_u=900$ and $k = \frac{x_u}{D}=2.0$).

Create a Python script named `example04.py` and type the following code in it.

```python
# File: example04.py

from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.rebar import RebarHYSD, LateralTie, RebarLayer, RebarGroup
from rcdesign.is456.section import RectColumnSection

b = 230
D = 450
csb = LSMStressBlock("LSM Compression")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)
L1 = RebarLayer(fe415, [16, 16, 16], 50)
L2 = RebarLayer(fe415, [16, 16], D / 2)
L3 = RebarLayer(fe415, [16, 16, 16], -50)
long_st = RebarGroup([L1, L2, L3])
lat_ties = LateralTie(fe415, 8, 150)
colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
xu = 900
k = xu / D  # k = 2 / 3
print(colsec.report(xu))
```

Run the example.
```bash
(env) $ python example04.py
RECTANGULAR COLUMN 230 x 450 xu = 900.00 (k = 2.00)
Concrete: fck = 20.00 N/mm^2, fd = 8.93 N/mm^2 Clear Cover: 35

   fck                 ecmin        ecmax Type     fsc1   fsc2       Cc       Mc
--------------------------------------------------------------------------------
 20.00            0.00127273   0.00254545    C     7.75   8.93   901.31   612.13
--------------------------------------------------------------------------------

    fy         Bars       xc       Strain Type      fsc    fcc   C (kN)  M (kNm)
--------------------------------------------------------------------------------
   415         3-16    50.00   0.00240404    C   342.45   8.93   201.18   171.00
   415         2-16   225.00   0.00190909    C   323.86   8.91   126.65    85.49
   415         3-16   400.00   0.00141414    C   282.83   8.17   165.67    82.84
--------------------------------------------------------------------------------
                                                                 493.49   339.32
                                                               =================
                                                                1394.81   951.45
```
