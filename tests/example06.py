"""Example 05

Section: Rectangular 230 x 500
Compression steel: 3 layer, Tension steel: 2 layers
Output: xu and report of the section.
"""
from scipy.optimize import brentq

from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    BentupBars,
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection
from rcdesign.utils import rootsearch

sb = LSMStressBlock("IS456 LSM")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer(fe415, [16, 16, 16], -35)
t2 = RebarLayer(fe415, [16, 16], -70)
c1 = RebarLayer(fe415, [16, 16], 35)
c2 = RebarLayer(fe415, [16, 16], 70)
c3 = RebarLayer(fe415, [12, 12], 100)
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150), BentupBars(fe415, [16, 16])])
long_st = RebarGroup([t2, c1, t1, c2])

sec = RectBeamSection(230, 500, sb, m20, long_st, sh_st, 25)
# xu = 110
xu = sec.xu(0.0035)
# print("x_u =", xu)
# Fc, Ft, Mc, Mt = sec.force_moment(xu, 0.0035)
# print(f"Fc = {Fc:.2f} Ft = {Ft:.2f} Mc = {Mc:.2f} Mt = {Mt:.2f}")
# print(sec)
s = sec.report(xu, 0.0035)
print("-" * 50)
print(s)
