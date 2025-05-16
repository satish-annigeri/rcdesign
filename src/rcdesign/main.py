from rcdesign import __version__
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


def main():
    print(f"rcdesign for RC Design as per IS456:2000 v{__version__}\n")
    sb = LSMStressBlock("LSM Flexure")
    m20 = Concrete("M20", 20)
    fe415 = RebarHYSD("Fe 415", 415)

    t1 = RebarLayer(fe415, [20, 16, 20], -35)
    steel = RebarGroup([t1])
    sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

    sec = RectBeamSection(230, 450, sb, m20, steel, sh_st, 25)
    xu = sec.xu(0.0035)
    print("Example 1\n")
    print(sec.report(xu, 0.0035))
    print(f"{'=' * 80}\n")

    # Doubly reinforced section
    sb = LSMStressBlock("IS456 LSM")
    m20 = Concrete("M20", 20)
    fe415 = RebarHYSD("Fe 415", 415)

    c1 = RebarLayer(fe415, [16, 16], 35)
    t1 = RebarLayer(fe415, [16, 16, 16], -35)
    t2 = RebarLayer(fe415, [16, 16], -70)
    steel = RebarGroup([c1, t1, t2])
    sh_st = ShearRebarGroup([Stirrups(fe415, 2, 8, 150)])

    sec = RectBeamSection(230, 450, sb, m20, steel, sh_st, 25)
    xu = sec.xu(0.0035)
    print("Example 2\n")
    print(sec.report(xu, 0.0035))
