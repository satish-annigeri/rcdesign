"""Example 05

Section: Rectangular 230 x 500
Compression steel: 3 layer, Tension steel: 2 layers
Output: xu and report of the section.
"""
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

t1 = RebarLayer(fe415, [16, 16, 16], -35)
t2 = RebarLayer(fe415, [16, 16], -70)
c1 = RebarLayer(fe415, [16, 16], 35)
c2 = RebarLayer(fe415, [16, 16], 70)
c3 = RebarLayer(fe415, [12, 12], 100)
steel = RebarGroup([c1, c2, c3, t1, t2])
sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

sec = RectBeamSection(230, 500, sb, m20, steel, sh_st, 25)
print(sec)
xu = sec.xu(0.0035)
print(sec.report(xu, 0.0035))
