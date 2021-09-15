from math import pi

from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete


class TestRebarGroup:
    def test_rebargroup01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        l1 = RebarLayer([16, 16, 16], 35)
        l2 = RebarLayer([16, 16], 70)
        grup = RebarGroup(fe415, [l1, l2])
        assert grup.area == 5 * pi * 16 ** 2 / 4

    def test_rebargroup02(self):
        fe415 = RebarHYSD("Fe 415", 415)
        l1 = RebarLayer([16, 16, 16], 35)
        l2 = RebarLayer([16, 16], 70)
        grup = RebarGroup(fe415, [l1, l2])
        assert grup.dc == (3 * 35 + 2 * 70) / (3 + 2)

    def test_rebargroup03(self):
        D = 450
        fe415 = RebarHYSD("Fe 415", 415)
        l1 = RebarLayer([16, 16, 16], -35)
        l1.calc_xc(D)
        l2 = RebarLayer([16, 16], -70)
        l2.calc_xc(D)
        grup = RebarGroup(fe415, [l1, l2])
        xu = 190
        # D_xu = D - xu
        ecu = 0.0035
        f, m = grup.force_tension(xu, ecu)
        f1, m1, _ = l1.force_tension(xu, fe415, ecu)
        f2, m2, _ = l2.force_tension(xu, fe415, ecu)
        assert (f == f1 + f2) and (m == m1 + m2)

    def test_rebargroup04(self):
        fe415 = RebarHYSD("Fe 415", 415)
        csb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
        conc = Concrete("M20", 20, csb)
        l1 = RebarLayer([16, 16, 16], 35)
        l2 = RebarLayer([16, 16], 70)
        grup = RebarGroup(fe415, [l1, l2])
        xu = 190
        ecu = 0.0035
        f, m = grup.force_compression(xu, conc, ecu)
        f1, m1, _ = l1.force_compression(xu, conc, fe415, ecu)
        f2, m2, _ = l2.force_compression(xu, conc, fe415, ecu)
        assert (f == f1 + f2) and (m == m1 + m2)

    def test_rebargroup05(self):
        fe415 = RebarHYSD("Fe 415", 415)
        c1 = RebarLayer([16, 16, 16], 35)
        c2 = RebarLayer([16, 16], 70)
        t1 = RebarLayer([16, 16, 16], -35)
        group = RebarGroup(fe415, [c1, c2, t1])
        xu = 190
        D = 450
        group.calc_xc(D)
        assert group.has_comp_steel(xu) and not group.has_comp_steel(25)

    def test_rebargroup06(self):
        fe415 = RebarHYSD("Fe 415", 415)
        c1 = RebarLayer([16, 16, 16], 35)
        c2 = RebarLayer([16, 16], 70)
        t1 = RebarLayer([16, 16, 16], -35)
        group = RebarGroup(fe415, [c1, c2, t1])
        D = 450
        xu = 70
        group.calc_xc(D)
        group.calc_stress_type(xu)
        assert group.layers[0].stress_type == "compression"
        assert group.layers[1].stress_type == "neutral"
        assert group.layers[2].stress_type == "tension"

    def test_rebargroup07(self):
        fe415 = RebarHYSD("Fe 415", 415)
        c1 = RebarLayer([16, 16, 16], 35)
        c2 = RebarLayer([16, 16], 70)
        t1 = RebarLayer([16, 16, 16], -35)
        group = RebarGroup(fe415, [c1, c2, t1])
        D = 450
        xu = 100
        group.calc_xc(D)
        assert group.area_tension(xu) == 3 * pi * 16 ** 2 / 4
        assert group.area_comp(xu) == 5 * pi * 16 ** 2 / 4

    def test_rebargroup08(self):
        fe415 = RebarHYSD("Fe 415", 415)
        c1 = RebarLayer([16, 16, 16], 35)
        c2 = RebarLayer([16, 16], 70)
        group = RebarGroup(fe415, [c1, c2])
        D = 450
        xu = 100
        group.calc_xc(D)
        assert group.dc_max(D) == (78, 450)

    def test_rebargroup09(self):
        fe415 = RebarHYSD("Fe 415", 415)
        c1 = RebarLayer([16, 16, 16], 35)
        c2 = RebarLayer([16, 16], 70)
        group = RebarGroup(fe415, [c1, c2])
        group.calc_xc(450)
        xbar = (3 * 35 + 2 * 70) / (3 + 2)
        assert group.centroid == xbar
