from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    ShearRebarGroup,
    Stirrups,
)
from rcdesign.is456.section import RectBeamSection

if __name__ == "__main__":
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
