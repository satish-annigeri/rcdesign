"""Example 05

Section: Rectangular 230 x 500
Compression steel: 3 layer, Tension steel: 2 layers
Output: xu and report of the section.
"""
from scipy.optimize import brentq

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import RectBeamSection
from rcdesign.utils import rootsearch


sb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
m20 = Concrete("M20", 20, sb)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer([16, 16, 16], -35)
t2 = RebarLayer([16, 16], -70)
c1 = RebarLayer([16, 16], 35)
c2 = RebarLayer([16, 16], 70)
c3 = RebarLayer([12, 12], 100)
# t_st = RebarGroup(fe415, [t1, t2])
# c_st = RebarGroup(fe415, [c1, c2])
t_st = None
c_st = None
sh_st = Stirrups(fe415, 2, 8, 150)
long_st = RebarGroup(fe415, [t2, c1, t1, c2])

sec = RectBeamSection(230, 500, m20, long_st, sh_st, 25)
# xu = 110
xu = sec.xu(0.0035)
print("x_u =", xu)
# Fc, Ft, Mc, Mt = sec.force_moment(xu, 0.0035)
# print(f"Fc = {Fc:.2f} Ft = {Ft:.2f} Mc = {Mc:.2f} Mt = {Mt:.2f}")
# print(sec)
s = sec.report(xu, 0.0035)
print("-" * 50)
print(s)
