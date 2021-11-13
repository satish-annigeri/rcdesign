from math import pi, sin, cos, isclose

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    BentupBars,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection


def test_rectbeam13a():
    fe415 = RebarHYSD("Fe 415", 415)
    csb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
    m20 = Concrete("M20", 20, csb)
    c1 = RebarLayer([16, 16], 35)
    t1 = RebarLayer([16, 16, 16], -35)

    long_st = RebarGroup(fe415, [c1, t1])
    sv = 150
    v_st = Stirrups(fe415, 2, 8, sv)
    alpha_deg = 45
    bup = BentupBars(fe415, [16, 16], alpha_deg, 0)
    sh_st = ShearRebarGroup([v_st, bup])
    b = 230
    D = 450
    rsec = RectBeamSection(b, D, m20, long_st, sh_st, 25)

    xu = 100
    d = rsec.eff_d(xu)
    # Manual calculation for shear reinforcement - Vertical stirrups
    Asv1 = pi / 4 * (2 * 8 ** 2)
    fd = 415 / 1.15
    Vus1 = fd * Asv1 * d / sv
    # Manual calculation for shear reinforcement - Bent-up bars
    alpha = alpha_deg * pi / 180
    Asv2 = pi / 4 * (2 * 16 ** 2)
    Vus2 = fd * Asv2 * sin(alpha)
    # Manual calculation for concrete
    pt = pi / 4 * (3 * 16 ** 2) * 100 / (230 * d)
    tauc = rsec.conc.tauc(pt)
    Vuc = tauc * b * d
    V = Vuc + Vus1 + Vus2
    # Method
    vuc, vus = rsec.Vu(xu)
    print("***", type(vus), vus, Vuc, Vus1, Vus2)
    assert isclose(vuc + sum(vus), V)


test_rectbeam13a()
