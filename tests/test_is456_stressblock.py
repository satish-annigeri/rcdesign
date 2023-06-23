from math import isclose, pi, sqrt
import pytest

# from sympy import symbols, nsimplify, integrate

from rcdesign.is456.stressblock import LSMStressBlock, WSMStressBlock
from rcdesign.is456 import ecy, ecu


def a_p(z1: float, z2: float, k: float) -> float:
    zcy = k - 3 / 7
    return (z2**2 - z1**2) / zcy - (z2**3 - z1**3) / (3 * zcy**2)


def m_p(z1: float, z2: float, k: float) -> float:
    zcy = k - 3 / 7
    m = (2 / 3) * (z2**3 - z1**3) / zcy - (1 / 4) * (z2**4 - z1**4) / (zcy**2)
    return m


def m_r(z1: float, z2: float) -> float:
    return (z2**2 - z1**2) / 2


@pytest.fixture
def sb():
    return LSMStressBlock()


@pytest.fixture
def sb_comp():
    return LSMStressBlock("LSM Compression")


class TestLSMStressBlock:
    def test_01(self, sb):
        assert sb._fc_(-0.0001) == 0
        assert sb._fc_(0.0036) == 0
        with pytest.raises(ValueError):
            assert sb._ec(-0.1)
        with pytest.raises(ValueError):
            assert sb._fc(0, -0.1)
        with pytest.raises(ValueError):
            assert sb.isvalid_ecmax(0.0036)
        with pytest.raises(ValueError):
            assert sb.isvalid_k(-0.1)

    def test_02(self, sb):
        k = 1.5
        assert sb.ec(k - 3 / 7, k) == 1
        assert sb.ec(k - 3 / 7, k) == 1
        assert sb.ec(k - 1, k) == (k - 1) / (k - 3 / 7)
        assert isclose(sb.ec(k, k), k / (k - 3 / 7))
        assert sb._ec(0) == 0.0

    def test_03(self, sb):
        k = 1.0
        assert sb.ec(0, k) == 0
        assert sb.ec(1, k) == ecu / ecy
        k = 0.9
        assert sb.ec(0, k) == 0
        assert isclose(sb.ec(k, k), 0.0035 / 0.002)
        assert isclose(sb.ec(0.5, k), 0.5 / k * 0.0035 / 0.002)

    def test_04(self, sb):
        ecy = 0.002
        ecu = 0.0035
        k = 1.5  # NA outside the section
        z = k - 1
        ec = z / (k - 3 / 7)
        assert sb.fc(z, k) == 2 * ec - ec**2
        z = k
        ec = z / (k - 3 / 7)
        assert sb.fc(k, k) == 2 * ec - ec**2 if ec < 1 else 1
        z = k / 2
        ec = z / (k - 3 / 7)
        assert sb.fc(z, k) == 2 * ec - ec**2 if ec < 1 else 1

        k = 1.0  # NA at edge of the section
        assert sb.fc(0, k) == 0
        assert sb.fc(1, k) == 1
        assert sb.fc(0.9, k) == 1
        assert sb.fc(4 / 7, k) == 1
        z = k / 2
        ec = z / k * ecu / ecy
        assert sb.fc(z, k) == 2 * ec - ec**2 if ec < 1 else 1

        k = 0.9  # NA inside the section
        assert sb.fc(0, k) == 0
        assert sb.fc(k, k) == 1
        assert sb.fc(4 / 7 * k, k) == 1
        assert sb.fc(k * 4 / 7 + 0.0001, k) == 1
        z = 0.45
        ec = z / k * ecu / ecy
        assert isclose(sb.fc(0.5 * k, k), 2 * ec - ec**2)

        k = 0
        assert sb.fc(z, k) == 0

    def test_05(self, sb):
        k = 1.5
        z1 = k - 1
        z2 = k - 3 / 7
        a = a_p(z1, z2, k)
        assert isclose(sb.C(k - 1, k, k), a + 3 / 7)
        assert isclose(sb.C(k, k - 1, k), a + 3 / 7)
        assert isclose(sb.C(k - 1, k - 3 / 7, k), a)
        with pytest.raises(ValueError):
            assert sb.C(k - 1 - 0.001, k, k)
        k = 1
        z1 = 0
        z2 = k * 4 / 7
        a = 2 / 3 * (z2 - z1)
        assert isclose(sb.C(z1, z2, k), a)
        assert isclose(sb.C(0, 1, k), a + 3 / 7)
        assert isclose(sb.C(4 / 7 * k, k, k), 3 / 7)
        with pytest.raises(ValueError):
            assert sb.C(k - 1 - 0.001, k, k)
        k = 0
        assert sb.C(z1, z2, k) == 0

    def test_06(self, sb):
        k = 1.5
        m1 = m_p(k - 1, k - 3 / 7, k)
        m2 = m_r(k - 3 / 7, k)
        assert isclose(sb.M(k - 1, k, k), m1 + m2)
        assert isclose(sb.M(k, k - 1, k), m1 + m2)
        assert isclose(sb.M(k - 1, k - 3 / 7, k), m1)
        assert isclose(sb.M(k - 3 / 7, k, k), m2)
        with pytest.raises(ValueError):
            assert sb.M(k - 1 - 0.001, k, k)

        k = 1
        m1 = 2 / 3 * 4 / 7 * (5 / 8 * 4 / 7)
        m2 = (3 / 7) * (4 / 7 + 1 / 2 * 3 / 7)
        assert isclose(sb.M(k - 1, k * 4 / 7, k), m1)
        assert isclose(sb.M(k * 4 / 7, k, k), m2)
        assert isclose(sb.M(k - 1, k, k), m1 + m2)
        with pytest.raises(ValueError):
            assert sb.M(k - 1 - 0.001, k, k)

        k = 0
        assert sb.M(0, 1, k) == 0


@pytest.fixture
def wsm_5_190():
    return WSMStressBlock(5.0, 190.0)


@pytest.fixture
def wsm_10_240():
    return WSMStressBlock(10.0, 240.0)


class TestWSMStressBlock:
    def test_01(self, wsm_5_190, wsm_10_240):
        fcbc = 5.0
        fst = 190.0
        assert wsm_5_190.fcbc == fcbc
        assert wsm_5_190.fst == fst
        assert isclose(wsm_5_190.m, 280.0 / (3 * fcbc))
        fcbc = 10.0
        fst = 240.0
        wsm_10_240.fcbc = 10.0
        assert wsm_10_240.fcbc == 10.0
        wsm_10_240.fst = 240.0
        assert wsm_10_240.fst == 240.0

    def test_02(self, wsm_5_190):
        fcbc = 5.0
        fst = 190.0
        m = wsm_5_190.m
        kb = (m * fcbc) / (m * fcbc + fst)
        assert isclose(wsm_5_190.kb(), kb)

    def test_03(self, wsm_5_190):
        fcbc = 5.0
        fst = 190.0
        d = 1.0
        m = wsm_5_190.m
        kb = (m * fcbc) / (m * fcbc + fst)
        jb = 1 - kb / 3.0
        assert isclose(wsm_5_190.jb(d), jb)

    def test_04(self, wsm_5_190):
        fcbc = 5.0
        b = 1.0
        d = 1.0
        xb = wsm_5_190.kb(d)
        Qb = b * xb * fcbc / 2.0 * (d - xb / 3.0)
        assert isclose(wsm_5_190.Qb(b, d), Qb)

    def test_05(self, wsm_5_190):
        fcbc = 5.0
        fst = 190.0
        d = 1.0
        xb = wsm_5_190.m * fcbc * d / (fst + wsm_5_190.m * fcbc)
        assert isclose(wsm_5_190.xb(d), xb)

    def test_06(self, wsm_5_190):
        b = 230.0
        d = 415.0
        Ast = 3 * pi / 4 * 16**2
        # Expected value
        ca = b / 2.0
        cb = wsm_5_190.m * Ast
        cc = -wsm_5_190.m * Ast * d
        expected = (-cb + sqrt(cb**2 - 4 * ca * cc)) / (2 * ca)

        assert isclose(wsm_5_190.x(b, d, Ast), expected)

    def test_07(self, wsm_5_190):
        b = 230.0
        d = 415.0
        Mb = wsm_5_190.Qb(b, d)
        # Expected value
        M = 0.8 * Mb
        x = (1.5 - sqrt(1.5**2 - (6 * M / (wsm_5_190.fcbc * b * d**2)))) * d
        Ast_exp = b * x * wsm_5_190.fcbc / (2 * wsm_5_190.fst)
        Asc_exp = 0.0
        Asc, Ast = wsm_5_190.reqd_Asc_Ast(b, d, 40, M)
        assert isclose(Asc, Asc_exp)
        assert isclose(Ast, Ast_exp)

        # Expected value
        M = 1.4 * Mb
        Asc, Ast = wsm_5_190.reqd_Asc_Ast(b, d, 40, M)
        assert Asc > 0
        assert Ast > 0
