from math import pi

from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete


class Test_RebarLayer:
    def test_rebarlayer01(self):
        l1 = RebarLayer(35, [16, 16, 16])
        assert l1.area == pi / 4 * (3 * 16 ** 2)

    def test_rebarlayer02(self):
        l1 = RebarLayer(35, [16, 16, 16])
        assert l1.dc == 35

    def test_rebarlayer03(self):
        l1 = RebarLayer(35, [25, 20, 16])
        assert l1.max_dia() == 25

    def test_rebarlayer04(self):
        l1 = RebarLayer(35, [16, 16, 16])
        assert l1.x(190) == 190 - 35

    def test_rebarlayer05(self):
        l1 = RebarLayer(35, [16, 16, 16])
        rebar = RebarHYSD("Fe 415", 415)
        xu = 190
        ecu = 0.0035
        es = ecu / xu * l1.x(xu)
        assert l1.fs(xu, rebar, ecu) == rebar.fs(es)

    def test_rebarlayer06(self):
        l1 = RebarLayer(35, [16, 16, 16])
        rebar = RebarHYSD("Fe 415", 415)
        D = 450
        xu = 190
        D_xu = D - xu
        ecu = 0.0035
        es = ecu / xu * l1.x(D_xu)
        f, m = l1.force_tension(xu, D_xu, rebar, ecu)
        assert (f == rebar.fs(es) * l1.area) and (m == f * (D_xu - 35))

    def test_rebarlayer07(self):
        l1 = RebarLayer(35, [16, 16, 16])
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
        f, m = l1.force_compression(xu, conc, rebar, ecu)
        ff = l1.area * (fsc - fcc)
        assert (f == ff) and (m == ff * (xu - 35))

    def test_rebarlayer08(self):
        l1 = RebarLayer(35, [20, 16, 20])
        s = l1.bar_list()
        assert s == "1-16;2-20"

    def test_rebarlayer09(self):
        l1 = RebarLayer(35, [20, 16, 20])
        l1.dc = 45
        assert l1.dc == 45
