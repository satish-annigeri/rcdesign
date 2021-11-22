from sympy import nsimplify
from math import isclose, sqrt
import pytest

from rcdesign import __version__
from rcdesign.is456.material.concrete import (
    MaximumStrainError,
    StressBlock,
    ConcreteStressBlock,
    Concrete,
    StressBlockError,
)


def test_version():
    assert __version__ == "0.2.0"


def parabolic_area(z1, z2, k=4 / 7):
    z1 /= k
    z2 /= k
    return ((z2 ** 2 - z1 ** 2) - (z2 ** 3 - z1 ** 3) / 3) * k


def rect_area(x1, x2):
    return x2 - x1


def area(x1, x2, k=4 / 7):
    if x1 > x2:
        x1, x2 = x2, x1
    if (x1 < 0) or (x2 > 1):
        return None
    a1 = a2 = 0.0
    if x1 < k:
        a1 = parabolic_area(x1, min(x2, k))
    if x2 > k:
        a2 = rect_area(max(k, x1), x2)
    return a1 + a2


def parabolic_moment(z1, z2, k=4 / 7):
    z1 /= k
    z2 /= k
    return (2 / 3 * (z2 ** 3 - z1 ** 3) - (z2 ** 4 - z1 ** 4) / 4) * k ** 2


def rect_moment(x1, x2):
    return (x2 ** 2 - x1 ** 2) / 2


def moment(x1, x2, k=4 / 7):
    if x1 > x2:
        x1, x2 = x2, x1
    if (x1 < 0) or (x2 > 1):
        return None
    m1 = m2 = 0.0
    if x1 <= k:
        m1 = parabolic_moment(x1, min(x2, k))
    if x2 >= k:
        m2 = rect_moment(max(k, x1), x2)
    return m1 + m2


def tauc(fck: float, pt: float):
    b = max((0.8 * fck) / (6.89 * pt), 1)
    tc = 0.85 * sqrt(0.8 * fck) * (sqrt(1 + 5 * b) - 1) / (6 * b)
    return tc


class TestCSB:
    # Verify stress
    def test_csb_01(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.stress(nsimplify(4 / 7), 0.0035), 1.0)

    def test_csb_02(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.stress(0, 0.0035), 0)

    def test_csb_03(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.stress(1, 0.002), 1.0)

    def test_csb_04(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        x = 0.5
        z = x / (0.002 / 0.0035)
        assert isclose(sb.stress(x, 0.0035), (2 * z - z ** 2))

    # Verify area of stress block
    def test_csb_05(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.area(0, 1, 0.0035), nsimplify(17 / 21))

    def test_csb_06(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.area(0, nsimplify(4 / 7), 0.0035), nsimplify(8 / 21))

    def test_csb_07(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.area(4 / 7, 1, 0.0035), nsimplify(3 / 7))

    def test_csb_08(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        k = 0.002 / 0.0035
        z1 = 0.2
        z2 = 0.4
        assert isclose(sb.area(z1, z2, 0.0035), area(z1, z2, k))

    # Verify first moment of area of stress block about NA
    def test_csb_09(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0, 1), moment(0, 1))

    def test_csb_10(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0, 0.002 / 0.0035), moment(0, 0.002 / 0.0035))

    def test_csb_11(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0.002 / 0.0035, 1), moment(0.002 / 0.0035, 1))

    def test_csb_12(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0.2, 0.4), moment(0.2, 0.4))

    def test_csb_13(self):
        k = 0.002 / 0.0035
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0, 1, 0.0035), moment(0, 1, k))

    def test_csb_14(self):
        k = 0.002 / 0.0035
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(1, 0, 0.0035), moment(0, 1, k))

    def test_csb_15(self):
        k = 0.002 / 0.0035
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert isclose(sb.moment(0.6, 1, 0.0035), moment(0.6, 1, k))

    def test_csb_16(self):
        with pytest.raises(TypeError):
            assert StressBlock("Stress Block").stress(0)

    def test_csb_17(self):
        sb = ConcreteStressBlock("IS456_LSFlexure")
        assert sb.validate_sb(0, 1) == (0, 1)
        assert sb.validate_sb(1, 0) == (0, 1)
        assert sb.validate_sb(0.2, 0.2) == (0.2, 0.2)
        with pytest.raises(StressBlockError):
            sb.validate_sb(0, 1.1)
        with pytest.raises(StressBlockError):
            sb.validate_sb(-0.1, 0.1)
        with pytest.raises(StressBlockError):
            sb.validate_sb(0.1, -0.1)
        try:
            sb.validate_sb(0, 1.1)
        except Exception as E:
            assert (
                E.__str__()
                == f"StressBlockError: Stress block distances ({0}, {1.1}) must be within 0 to 1"
            )

    # Verify MaximumStrainException
    def test_csb18(self):
        csb = ConcreteStressBlock("IS456 LSM")
        ecmax = 0.0036
        with pytest.raises(MaximumStrainError):
            assert csb.stress(0.1, 0.0036)


class TestConcrete:
    # Verify design stress
    def test_conc01(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.fd, 0.67 * 20 / 1.5)

    # Verify elastic modulus
    def test_conc02(self):
        csb = ConcreteStressBlock("IS456 LSM")
        fck = 20
        m20 = Concrete("M20", fck, csb)
        assert isclose(m20.Ec, 5000 * fck ** 0.5)

    # Verify stress at highly compressed edge
    def test_conc03(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.fc(1) * m20.fd, m20.fd)

    # Verify stress at strain = 0.002
    def test_conc04(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.fc(4 / 7) * m20.fd, m20.fd)

    # Verify stress at mid-height of neutral axis (in parabolic region)
    def test_conc05(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        z = 0.5 / (0.002 / 0.0035)
        assert isclose(m20.fc(0.5), (2 * z - z ** 2))

    # Verify maximum shear stress with shear reinforcement
    def test_conc06(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert m20.tauc_max() == 2.8

    # Verify compression force for full depth of neutral axis
    def test_conc07(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.area(0, 1, m20.fd), area(0, 1) * m20.fd)

    # Verify moment about NA of compression force for full depth of neutral axis
    def test_conc08(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.moment(0, 1, m20.fd), moment(0, 1) * m20.fd)

    # Verify distance of centroid of compression force for
    # full depth of neutral axis
    def test_conc09(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.centroid(0, 1, m20.fd), moment(0, 1) / area(0, 1))

    # Verify tau_c
    def test_conc10(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        pt = 0.25
        assert isclose(m20.tauc(pt), tauc(m20.fck, pt))

    # Verify invalid range for x1 and x2
    def test_conc11(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        with pytest.raises(StressBlockError):
            m20.area(0, 1.1)

    # Verify reversed values of x1 and x2
    def test_conc12(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert m20.area(1, 0) == m20.area(0, 1)

    # Verify invalid range for x1 and x2
    def test_conc13(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert isclose(m20.area(0.6, 1, m20.fd), area(0.6, 1) * m20.fd)

    # Verify invalid range for x1 and x2
    def test_conc14(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        with pytest.raises(StressBlockError):
            m20.moment(0, 1.1)

    # Verify ecy
    def test_conc15(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert m20.ecy == 0.002

    # Verify ecu
    def test_conc16(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert m20.ecu == 0.0035

    # Verify fd
    def test_conc17(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        assert m20.fd == m20.fck * 0.67 / m20.gamma_m

    # Verify fc for invalid range of x1 and x2
    def test_conc18(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        with pytest.raises(ValueError):
            assert m20.fc(1.1)

    # Verify tau_c
    def test_conc19(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m10 = Concrete("M10", 10, csb)
        assert isclose(m10.tauc_max(), 0.0)

    # Verify tau_c
    def test_conc20(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m40 = Concrete("M40", 40, csb)
        m45 = Concrete("M45", 45, csb)
        assert isclose(m45.tauc_max(), m40.tauc_max())

    # Verify tau_c
    def test_conc21(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        pt = 0.10
        assert isclose(m20.tauc(pt), tauc(m20.fck, 0.15))

    # Verify tau_c
    def test_conc22(self):
        csb = ConcreteStressBlock("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        pt = 3.1
        assert isclose(m20.tauc(pt), tauc(m20.fck, 3.0))
