# import numpy as np`
# import matplotlib.pyplot as plt
from scipy.optimize import brentq
from rcdesign.utils import rootsearch

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import (
    RebarHYSD, RebarLayer, RebarGroup, Stirrups)
from rcdesign.is456.section import RectBeamSection

from rcdesign import __version__

print(f'Analysis of Reinforced Concrete Sections v{__version__}\n')
# Create materials
# Concrete: M20 grade concrete in flexure Limit State Method
sb_lsm_flex = ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035)
m20 = Concrete('M20', 20, sb_lsm_flex)
# HYSD reinforcement bars: Fe 415 grade
fe415 = RebarHYSD('Fe 415', 415)
# Two layers of tension reinforcement
t1 = RebarLayer(35, [16, 16, 16])   # 3-16mm dia @ 35mm from tension edge
t2 = RebarLayer(70, [16, 16])       # 2-16mm dia @ 70mm from tension edge
# One layer of compression reinforcement
c1 = RebarLayer(35, [16, 16])       # 2-16mm dia @ 35mm from compression edge
# Group of tension bars
t_st = RebarGroup(fe415, [t1, t2])  # Sequence is unimportant
# Group of compression bars
c_st = RebarGroup(fe415, [c1])
# Ahear reinforcement in the form of vertical stirrups
shear_st = Stirrups(fe415, 2, 8, 150, 90)
# Rectangular beam section
rect_sec = RectBeamSection(230, 450, m20, t_st, c_st, shear_st, 25)
print(rect_sec)
print()

# Analysis of a rectangular beam section of size 230x450 mm overall
xu = 150  # Assumed depth of neutral axis. May not correspond to equilibrium
print(f'Analysis of section for xu = {xu}')
print(f'Compression (C): {rect_sec.C(xu, 0.0035)[0]/1e3:10.2f} kN')
print(f'    Tension (T): {rect_sec.T(xu, 0.0035)[0]/1e3:10.2f} kN')
print(f'          C - T: {rect_sec.C_T(xu, 0.0035)/1e3:10.2f} kN')
print()

# Locate the depth of neutral axis to satisfy equilibrium
print('Location of neutral axis for equilibrium')
# Bracket the position of neutral axis
x1, x2 = rootsearch(rect_sec.C_T, 50, 400, 10, rect_sec.conc.ecu)
print(f'Neutral axis lies between {x1:.2f} and {x2:.2f} from compression edge')

# Locate neutral axis iteratively by bisection
xu = brentq(rect_sec.C_T, x1, x2, args=(rect_sec.conc.ecu,), xtol=1e-4)
print(f'Depth of neutral axis: {xu:.2f}')
print()

# Report of analysis of the section for xu corresponding to equilibriu,
rect_sec.report(xu, rect_sec.conc.ecu)
print()

# Shear capacity of section
Vu = rect_sec.Vu()
print(f'Ultimate shear capacity (kN): {Vu/1e3:.2f}')

# concsb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
# print(concsb.ecy)
# conc = Concrete('M20', 20, concsb)
# t1 = RebarLayer(35, [16, 16, 16])
# t2 = RebarLayer(70, [16, 16])
# t_st = RebarGroup(RebarHYSD('Fe 415', 415), [t1, t2])
# c_st = RebarGroup(RebarHYSD('Fe 415', 415), [c1])
# sec_st = RebarHYSD('Fe415', 415)
# shear_steel = Stirrups(RebarHYSD('Fe 415', 415), 2, 8, 90, 125)
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)
# shear_steel.nlegs = 4
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)
# shear_steel.bar_dia = 10
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)

# tsec = FlangedBeamSection(230, 450, 1000, 150, conc, t_st, None, shear_steel, 25)

# xu = 50.16570748
# xu = 150
# print(f"xu = {xu} C = {tsec.C(xu, 0.0035)}")
# print(f"xu = {xu} T = {tsec.T(xu, 0.0035)}")

# xumax = tsec.xumax(tsec.eff_d())
# xumax = 190
# print('xumax =', xumax)
# print(f"xu = {xumax} C = {tsec.C(xumax, 0.0035)} Mr = {tsec.Mr(xumax, 0.0035)}")

# if xumax > tsec.Df:
#     print(f"xu = {xumax} Mr = {tsec.Mr(xumax, 0.0035)}")

# x = np.linspace(5, xumax, 5)
# for xx in x:
#     print(f"xu = {xx:8.2f} Mr = {tsec.Mr(xx, 0.0035)/1e6:8.2f}")

