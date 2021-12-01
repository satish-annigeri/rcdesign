"""Example 01

Section: Rectangular 230 x 450
Compression steel: Nil, Tension steel: 1 layer
Output: xu and report of the section.
"""

from rcdesign.is456.material.concrete import ConcreteLSMFlexure, Concrete
from rcdesign.is456.material.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection


sb = ConcreteLSMFlexure("IS456 LSM")
m20 = Concrete("M20", 20, sb)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer([20, 16, 20], -35)
steel = RebarGroup(fe415, [t1])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 450, m20, steel, sh_st, 25)
print(sec)
xu = sec.xu(0.0035)
print(f"xu = {xu:.2f}")
print(sec.report(xu, 0.0035))

m25 = Concrete("M25", 25, sb)
fe500 = RebarHYSD("Fe 500", 500)
l1 = RebarLayer([16, 16, 16, 16, 16, 16, 10], -58)
main_steel = RebarGroup(fe500, [l1])
shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 6, 300)])
sec2 = RectBeamSection(1000, 450, m25, main_steel, shear_steel, 50)
xu2 = sec2.xu(0.0035)
print(sec2.report(xu2, 0.0035))
