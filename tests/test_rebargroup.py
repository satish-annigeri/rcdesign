from math import pi

from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete


class TestRebarGroup:
    def test_rebargroup01(self):
        fe415 = RebarHYSD('Fe 415', 415)
        l1 = RebarLayer(35, [16, 16, 16])
        l2 = RebarLayer(70, [16, 16])
        grup = RebarGroup(fe415, [l1, l2])
        assert grup.area() == 5 * pi * 16**2 / 4

    def test_rebargroup02(self):
        fe415 = RebarHYSD('Fe 415', 415)
        l1 = RebarLayer(35, [16, 16, 16])
        l2 = RebarLayer(70, [16, 16])
        grup = RebarGroup(fe415, [l1, l2])
        assert grup.dc == (3 * 35 + 2 * 70) / (3 + 2)

    def test_rebargroup03(self):
        fe415 = RebarHYSD('Fe 415', 415)
        l1 = RebarLayer(35, [16, 16, 16])
        l2 = RebarLayer(70, [16, 16])
        grup = RebarGroup(fe415, [l1, l2])
        D = 450
        xu = 190
        D_xu = D - xu
        ecu = 0.0035
        f, m = grup.force_tension(xu, D_xu, ecu)
        f1, m1 = l1.force_tension(xu, D_xu, fe415, ecu)
        f2, m2 = l2.force_tension(xu, D_xu, fe415, ecu)
        assert (f == f1 + f2) and (m == m1 + m2)

    def test_rebargroup04(self):
        fe415 = RebarHYSD('Fe 415', 415)
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        conc = Concrete('M20', 20, csb)
        l1 = RebarLayer(35, [16, 16, 16])
        l2 = RebarLayer(70, [16, 16])
        grup = RebarGroup(fe415, [l1, l2])
        xu = 190
        ecu = 0.0035
        f, m = grup.force_compression(xu, conc, ecu)
        f1, m1 = l1.force_compression(xu, conc, fe415, ecu)
        f2, m2 = l2.force_compression(xu, conc, fe415, ecu)
        assert (f == f1 + f2) and (m == m1 + m2)
