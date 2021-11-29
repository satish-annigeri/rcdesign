"""Example 03

Section: Rectangular 230 x 450
Compression steel: 1 layer, Tension steel: 2 layers
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

c1 = RebarLayer([16, 16], 35)
t1 = RebarLayer([16, 16, 16], -35)
t2 = RebarLayer([16, 16], -70)
steel = RebarGroup(fe415, [c1, t1, t2])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 450, m20, steel, sh_st, 25)
print(sec)
xu = sec.xu(0.0035)
print(sec.report(xu, 0.0035))
