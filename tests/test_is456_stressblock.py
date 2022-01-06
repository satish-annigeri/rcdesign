from math import isclose
import pytest
from sympy import symbols, nsimplify, integrate

from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456 import ecy, ecu


def a_p(z1: float, z2: float, k: float) -> float:
    zcy = k - 3 / 7
    return (z2 ** 2 - z1 ** 2) / zcy - (z2 ** 3 - z1 ** 3) / (3 * zcy ** 2)


def m_p(z1: float, z2: float, k: float) -> float:
    zcy = k - 3 / 7
    m = (2 / 3) * (z2 ** 3 - z1 ** 3) / zcy - (1 / 4) * (z2 ** 4 - z1 ** 4) / (zcy ** 2)
    return m


def m_r(z1: float, z2: float) -> float:
    return (z2 ** 2 - z1 ** 2) / 2


class TestLSMStressBlock:
    def test_01(self):
        sb = LSMStressBlock()
        k = 1.5

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

    def test_02(self):
        sb = LSMStressBlock("LSM Compression")
        k = 1.5
        assert sb.ec(k - 3 / 7, k) == 1
        assert sb.ec(k - 3 / 7, k) == 1
        assert sb.ec(k - 1, k) == (k - 1) / (k - 3 / 7)
        assert isclose(sb.ec(k, k), k / (k - 3 / 7))
        assert sb._ec(0) == 0.0

    def test_03(self):
        sb = LSMStressBlock("LSM Compression")

        k = 1.0
        assert sb.ec(0, k) == 0
        assert sb.ec(1, k) == ecu / ecy
        k = 0.9
        assert sb.ec(0, k) == 0
        assert isclose(sb.ec(k, k), 0.0035 / 0.002)
        assert isclose(sb.ec(0.5, k), 0.5 / k * 0.0035 / 0.002)

    def test_04(self):
        ecy = 0.002
        ecu = 0.0035
        sb = LSMStressBlock("LSM Compression")
        k = 1.5  # NA outside the section
        z = k - 1
        ec = z / (k - 3 / 7)
        assert sb.fc(z, k) == 2 * ec - ec ** 2
        z = k
        ec = z / (k - 3 / 7)
        assert sb.fc(k, k) == 2 * ec - ec ** 2 if ec < 1 else 1
        z = k / 2
        ec = z / (k - 3 / 7)
        assert sb.fc(z, k) == 2 * ec - ec ** 2 if ec < 1 else 1

        k = 1.0  # NA at edge of the section
        assert sb.fc(0, k) == 0
        assert sb.fc(1, k) == 1
        assert sb.fc(0.9, k) == 1
        assert sb.fc(4 / 7, k) == 1
        z = k / 2
        ec = z / k * ecu / ecy
        assert sb.fc(z, k) == 2 * ec - ec ** 2 if ec < 1 else 1

        k = 0.9  # NA inside the section
        assert sb.fc(0, k) == 0
        assert sb.fc(k, k) == 1
        assert sb.fc(4 / 7 * k, k) == 1
        assert sb.fc(k * 4 / 7 + 0.0001, k) == 1
        z = 0.45
        ec = z / k * ecu / ecy
        assert isclose(sb.fc(0.5 * k, k), 2 * ec - ec ** 2)

    def test_05(self):
        sb = LSMStressBlock("LSM Compression")
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

    def test_06(self):
        sb = LSMStressBlock("LSM Compression")
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
