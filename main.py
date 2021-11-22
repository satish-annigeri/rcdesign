# import numpy as np`
# import matplotlib.pyplot as plt
from scipy.optimize import brentq
from rcdesign.utils import rootsearch

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    ShearRebarGroup,
    Stirrups,
)
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection

from rcdesign import __version__

print(f"Analysis of Reinforced Concrete Sections v{__version__}\n")
# Create materials
# Concrete: M20 grade concrete in flexure Limit State Method
sb_lsm_flex = ConcreteStressBlock("IS456:2000 LSM")
m20 = Concrete("M20", 20, sb_lsm_flex)
# HYSD reinforcement bars: Fe 415 grade
fe415 = RebarHYSD("Fe 415", 415)
# Two layers of tension reinforcement
t1 = RebarLayer([16, 16, 16], -35)  # 3-16mm dia @ 35mm from tension edge
t2 = RebarLayer([16, 16], -70)  # 2-16mm dia @ 70mm from tension edge
# One layer of compression reinforcement
c1 = RebarLayer([16, 16], 35)  # 2-16mm dia @ 35mm from compression edge
# Group of tension bars
long_st = RebarGroup(fe415, [c1, t1, t2])  # Sequence is unimportant
# Shear reinforcement in the form of vertical stirrups
shear_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150, 90)])  # 2 legged 8# @ 150 c/c
# Rectangular beam section
rect_sec = RectBeamSection(230, 450, m20, long_st, shear_st, 25)
print(rect_sec)
print()

# # Analysis of a rectangular beam section of size 230x450 mm overall
# xu = 150.0  # Assumed depth of neutral axis. May not correspond to equilibrium
# print(f"Analysis of section for xu = {xu}")
# print(f"Compression (C): {rect_sec.C(xu, 0.0035)[0]/1e3:10.2f} kN")
# print(f"    Tension (T): {rect_sec.T(xu, 0.0035)[0]/1e3:10.2f} kN")
# print(f"          C - T: {rect_sec.C_T(xu, 0.0035)/1e3:10.2f} kN")
# print()

# # Locate the depth of neutral axis to satisfy equilibrium
# print("Location of neutral axis for equilibrium")
# # Bracket the position of neutral axis
# x1, x2 = rootsearch(rect_sec.C_T, 50, 400, 10, rect_sec.conc.ecu)
# print(f"Neutral axis lies between {x1:.2f} and {x2:.2f} from compression edge")

# # Locate neutral axis iteratively by bisection
# xu = brentq(rect_sec.C_T, x1, x2, args=(rect_sec.conc.ecu,), xtol=1e-4)
# print(f"Depth of neutral axis: {xu:.2f}")
# print()

# # Report of analysis of the section for xu corresponding to equilibriu,
# rect_sec.report(xu, rect_sec.conc.ecu)

# # Flanged section
# long_st = RebarGroup(fe415, [t1, t2])
# tsec = FlangedBeamSection(230, 450, 1000, 150, m20, long_st, shear_st, 25)
# xu = tsec.xu(0.0035)
# # print(f"xu = {xu:.2f} Mu = {Mu/1e6:.2f}")
# print(tsec.report(xu, 0.0035))
