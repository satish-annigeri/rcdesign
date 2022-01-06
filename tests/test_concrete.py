from math import isclose, sqrt
import pytest


from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456 import ecy, ecu
from rcdesign.is456.concrete import Concrete


class TestConcrete:
    def test_01(self):
        m20 = Concrete("M20", 20)
        assert m20.Ec == 5000 * sqrt(m20.fck)
        assert m20.fd == m20.fck * 0.67 / m20.gamma_m

    def test_02(self):
        def tauc(pt, fck):
            beta = max(1, 0.8 * fck / (6.89 * pt))
            tc = ((0.85 * sqrt(0.8 * fck)) * (sqrt(1 + 5 * beta) - 1)) / (6 * beta)
            return tc

        m20 = Concrete("M20", 20)
        m30 = Concrete("M30", 30)
        assert m20.tauc(0.2) == tauc(0.2, m20.fck)
        assert m30.tauc(0.3) == tauc(0.3, m30.fck)
        assert m20.tauc(0.5) == tauc(0.5, m20.fck)
        assert m20.tauc(0.1) == tauc(0.15, m20.fck)
        assert m20.tauc(3.1) == tauc(3.0, m20.fck)

    def test_03(self):
        assert Concrete("M15", 15).tauc_max() == 2.5
        assert Concrete("M20", 20).tauc_max() == 2.8
        assert Concrete("M25", 25).tauc_max() == 3.1
        assert Concrete("M30", 30).tauc_max() == 3.5
        assert Concrete("M35", 35).tauc_max() == 3.7
        assert Concrete("M40", 40).tauc_max() == 4.0
        assert Concrete("M50", 50).tauc_max() == 4.0
        assert Concrete("M10", 10).tauc_max() == 0
