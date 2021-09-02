from sympy import nsimplify, Rational
from math import isclose

from rcdesign import __version__
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete


def test_version():
    assert __version__ == '0.1.0'


def parabolic_area(z1, z2, k=4/7):
    z1 /= k
    z2 /= k
    return ((z2**2 - z1**2) - (z2**3 - z1**3) / 3) * k

def parabolic_moment(z1, z2, k=4/7):
    z1 /= k
    z2 /= k
    return (2 / 3 * (z2**3 - z1**3) - (z2**4 - z1**4) / 4) * k**2

def rect_area(x1, x2):
    return x2 - x1

def rect_moment(x1, x2):
    return (x2**2 - x1**2) / 2

def area(x1, x2, k=4/7):
    if x1 > x2:
        x1, x2 = x2, x1
    if (x1 < 0) or (x2 > 1):
        return None
    a1 = a2 = 0.0
    if x1 <= k: a1 = parabolic_area(x1, min(x2, k))
    if x2 >= k: a2 = rect_area(min(k, x1), x2)
    return a1 + a2

def moment(x1, x2, k=4/7):
    if x1 > x2:
        x1, x2 = x2, x1
    if (x1 < 0) or (x2 > 1):
        return None
    m1 = m2 = 0.0
    if x1 <= k: m1 = parabolic_moment(x1, min(x2, k))
    if x2 >= k: m2 = rect_moment(max(k, x1), x2)
    print('***', m1, m2, m1+m2)
    return m1 + m2
class TestCSB():
    # Verify stress
    def test_csb_01(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.stress(nsimplify(4 / 7), 0.0035), 1.0)

    def test_csb_02(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.stress(0, 0.0035), 0)

    def test_csb_03(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.002)
        assert isclose(sb.stress(1, 0.0035), 1.0)

    def test_csb_04(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        x = 0.5
        z = x / (0.002 / 0.0035)
        assert isclose(sb.stress(x, 0.0035), (2 * z - z**2))

    # Verify area of stress block
    def test_csb_05(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.area(0, 1, 0.0035), nsimplify(17 / 21))

    def test_csb_06(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.area(0, nsimplify(4/7), 0.0035), nsimplify(8 / 21))

    def test_csb_07(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.area(4/7, 1, 0.0035), nsimplify(3 / 7))

    def test_csb_08(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        k = 0.002 / 0.0035
        z1 = 0.2
        z2 = 0.4
        assert isclose(sb.area(z1, z2, 0.0035), area(z1, z2, k))

    # Verify first moment of area of stress block about NA
    def test_csb_09(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.moment(0, 1), moment(0, 1))

    def test_csb_10(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.moment(0, 0.002/0.0035), moment(0, 0.002/0.0035))

    def test_csb_11(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.moment(0.002/0.0035, 1), moment(0.002/0.0035, 1))

    def test_csb_12(self):
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.moment(0.2, 0.4), moment(0.2, 0.4))

    def test_csb_12(self):
        k = 0.002 / 0.0035
        sb = ConcreteStressBlock('IS456_LSFlexure', 0.002, 0.0035)
        assert isclose(sb.moment(0, 1, 0.0035), moment(0, 1, k))


class TestConcrete:
    def test_conc01(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        m20 = Concrete('M20', 20, csb)
        assert isclose(m20.fd, 0.67 * 20 / 1.5)

    def test_conc02(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        fck = 20
        m20 = Concrete('M20', fck, csb)
        assert isclose(m20.Ec, 5000 * fck**0.5)

    def test_conc03(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        m20 = Concrete('M20', 20, csb)
        assert isclose(m20.fc(1) * m20.fd, m20.fd)

    def test_conc04(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        m20 = Concrete('M20', 20, csb)
        assert isclose(m20.fc(4/7) * m20.fd, m20.fd)

    def test_conc05(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        m20 = Concrete('M20', 20, csb)
        z = 0.5 / (0.002 / 0.0035)
        assert isclose(m20.fc(0.5), (2*z - z**2))

    def test_conc06(self):
        csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
        m20 = Concrete('M20', 20, csb)
        assert m20.tauc_max() == 2.8