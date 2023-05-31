import rcdesign.is456.constants as const
from fractions import Fraction


class TestConstants:
    def test_01(self):
        assert const.gamma_c == Fraction(3, 2)
        assert const.gamma_s == Fraction(115, 100)
        assert const.ecu == 0.0035
        assert const.ecy == 0.002
        assert const.Es == 2e5
        assert const.fdc == Fraction(2, 3) / Fraction(3, 2)
        assert const.fds == 1 / Fraction(115, 100)
        assert const._A1 == Fraction(2, 3) * Fraction(4, 7)
        assert const._A2 == Fraction(3, 7)
        assert const.k1 == Fraction(17, 21) * Fraction(4, 9)
        assert const.k2 == Fraction(99, 238)
