"""Example 04

Section: Rectangular 230 x 500
Compression steel: 2 layer, Tension steel: 2 layers
Output: xu and report of the section.
"""
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.section import RectBeamSection


sb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
m20 = Concrete("M20", 20, sb)
fe415 = RebarHYSD("Fe 415", 415)

t1 = RebarLayer(35, [16, 16, 16])
t2 = RebarLayer(70, [16, 16])
t_st = RebarGroup(fe415, [t1, t2])
c1 = RebarLayer(35, [16, 16])
c2 = RebarLayer(70, [16, 16])
c_st = RebarGroup(fe415, [c1, c2])
sh_st = Stirrups(fe415, 2, 8, 150)

sec = RectBeamSection(230, 500, m20, t_st, c_st, sh_st, 25)
print(sec)
xu = sec.xu(0.0035)
sec.report(xu, 0.0035)
