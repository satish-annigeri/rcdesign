# Krishna Raju, N. and Pranesh, R.N., Reinforced Concrete Design, 6.3.5, pp. 89,

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import FlangedBeamSection

csb = ConcreteStressBlock("IS456 LSM")
m25 = Concrete("M25", 25, csb)
fe415 = RebarHYSD("Fe 415", 415)
t1 = RebarLayer([20, 20, 20], -35)
t2 = RebarLayer([18, 18], -70)
main_steel = RebarGroup(fe415, [t1, t2])
shear_steel = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])
tsec = FlangedBeamSection(300, 475, 800, 150, m25, main_steel, shear_steel, 25)
xu = tsec.xu(0.0035)
print(tsec.report(xu, 0.0035))
