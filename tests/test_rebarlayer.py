from math import pi

from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete


class TestRebarLayer:
    def test_rebarlayer01(self):
        l1 = RebarLayer([16, 16, 16], 35)
        assert l1.area == pi / 4 * (3 * 16 ** 2)

    def test_rebarlayer02(self):
        l1 = RebarLayer([16, 16, 16], 35)
        assert l1.dc == 35

    def test_rebarlayer03(self):
        l1 = RebarLayer([25, 20, 16], 35)
        assert l1.max_dia() == 25

    def test_rebarlayer04(self):
        l1 = RebarLayer([16, 16, 16], 35)
        l1.calc_xc(450)
        assert l1.x(190) == 190 - 35

    def test_rebarlayer05(self):
        l1 = RebarLayer([16, 16, 16], 35)
        rebar = RebarHYSD("Fe 415", 415)
        xu = 190
        ecu = 0.0035
        es = ecu / xu * l1.x(xu)
        assert l1.fs(xu, rebar, ecu) == rebar.fs(es)

    def test_rebarlayer06(self):
        D = 450
        l1 = RebarLayer([16, 16, 16], 35)
        l1.calc_xc(D)
        rebar = RebarHYSD("Fe 415", 415)
        xu = 190
        D_xu = D - xu
        ecu = 0.0035
        es = ecu / xu * l1.x(xu)
        f, m, _ = l1.force_tension(xu, rebar, ecu)
        assert (f == rebar.fs(es) * l1.area) and (m == f * (xu - 35))

    def test_rebarlayer07(self):
        l1 = RebarLayer([16, 16, 16], 35)
        l1.calc_xc(450)
        rebar = RebarHYSD("Fe 415", 415)
        csb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
        conc = Concrete("M20", 20, csb)
        xu = 190
        x = l1.x(xu)
        ecu = 0.0035
        es = ecu / xu * l1.x(xu)
        fsc = rebar.fs(es)
        fcc = conc.fc(x / xu) * conc.fd
        print(es, fsc, fcc)
        f, m, _ = l1.force_compression(xu, conc, rebar, ecu)
        ff = l1.area * (fsc - fcc)
        assert (f == ff) and (m == ff * (xu - 35))

    def test_rebarlayer08(self):
        l1 = RebarLayer([20, 16, 20], 35)
        s = l1.bar_list()
        assert s == "1-16;2-20"

    def test_rebarlayer09(self):
        l1 = RebarLayer([20, 16, 20], 35)
        l1.dc = 45
        assert l1.dc == 45

    def test_rebarlayer10(self):
        l1 = RebarLayer([20, 16, 20], 70)
        l2 = RebarLayer([20, 16, 20], 35)
        l3 = RebarLayer([20, 16, 20], 100)
        l4 = RebarLayer([20, 16, 20], 35)
        l1.calc_xc(450)
        l2.calc_xc(450)
        l3.calc_xc(450)
        l4.calc_xc(450)

        assert (
            l1 > l2
            and (l2 < l3)
            and (l2 == l4)
            and (l2 <= l1)
            and (l2 <= l4)
            and (l4 >= l2)
            and (l2 != l3)
        )

    def test_rebarlayer11(self):
        D = 450
        l1 = RebarLayer([20, 16, 20], 70)
        l1.calc_xc(D)
        assert l1.xc == 70
        l1 = RebarLayer([20, 16, 20], -70)
        l1.calc_xc(D)
        assert l1.xc == D - 70

    def test_rebarlayer12(self):
        D = 450
        xu = 100
        l1 = RebarLayer([20, 16, 20], 100)
        l1.calc_xc(D)
        assert l1.calc_stress_type(xu) == "neutral"
