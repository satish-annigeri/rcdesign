from math import isclose
import numpy as np

from rcdesign.is456.material.rebar import RebarMS, RebarHYSD

def get_fs(fd, es, fd1, fd2, es1, es2, Es=2e5):
    x = fd1 * fd / Es + es1 + es
    y1 = fd1 * fd; y2 = fd2 * fd
    x1 = y1 / Es + es1; x2 = y2 / Es + es2
    # print(x, x1, x2, y1, y2)
    return y1 + (y2 - y1) / (x2 - x1) * (x - x1)

class Test_rebar:
    # Verify stress in linear elastic region
    def test_rebar01(self):
        ms = RebarMS('MS', 250)
        assert isclose(ms.fs(0.001), 0.001 * 2e5)

    def test_rebar02(self):
        ms = RebarMS('MS', 250)
        assert isclose(ms.fs(ms.fy / ms.gamma_m / ms.Es), ms.fd)

    def test_rebar03(self):
        ms = RebarMS('MS', 250)
        assert isclose(ms.fs(ms.fy / ms.gamma_m / ms.Es + 0.0001), ms.fd)

    def test_rebar04(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = fe415.fy / fe415.gamma_m / fe415.Es + 0.0021
        assert isclose(fe415.fs(es), fe415.fd)

    def test_rebar05(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = 0.8 * fe415.fy / fe415.gamma_m / fe415.Es
        assert isclose(fe415.fs(es), 0.8 * fe415.fy / fe415.gamma_m)

    def test_rebar06(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = 0.85 * fe415.fy / fe415.gamma_m / fe415.Es + 0.0001
        assert isclose(fe415.fs(es), 0.85 * fe415.fd)

    def test_rebar07(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = 0.9 * fe415.fy / fe415.gamma_m / fe415.Es + 0.0003
        assert isclose(fe415.fs(es), 0.9 * fe415.fd)

    def test_rebar08(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = 0.95 * fe415.fy / fe415.gamma_m / fe415.Es + 0.0007
        assert isclose(fe415.fs(es), 0.95 * fe415.fd)

    def test_rebar09(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = 0.975 * fe415.fy / fe415.gamma_m / fe415.Es + 0.001
        assert isclose(fe415.fs(es), 0.975 * fe415.fd)

    def test_rebar10(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = fe415.fy / fe415.gamma_m / fe415.Es + 0.002
        assert isclose(fe415.fs(es), fe415.fd)

    # Verify stress for strain between 0.8 and 0.85 times fd
    def test_rebar11(self):
        fe415 = RebarHYSD('Fe 415', 415)
        Es = fe415.Es
        x = 0.8 * fe415.fd / Es + 0.00005
        y = get_fs(fe415.fd, 0.00005, 0.8, 0.85, 0, 0.0001)
        assert isclose(fe415.fs(x), y)

    # Verify stress for strain between 0.85 and 0.9 times fd
    def test_rebar12(self):
        fe415 = RebarHYSD('Fe 415', 415)
        Es = fe415.Es
        x = 0.85 * fe415.fd / Es + 0.0001 + 0.00005
        y = get_fs(fe415.fd, 0.00005, 0.85, 0.9, 0.0001, 0.0003)
        assert isclose(fe415.fs(x), y)

    # Verify stress for strain between 0.9 and 0.95 times fd
    def test_rebar13(self):
        fe415 = RebarHYSD('Fe 415', 415)
        Es = fe415.Es
        x = 0.9 * fe415.fd / Es + 0.0003 +0.00005
        y = get_fs(fe415.fd, 0.00005, 0.9, 0.95, 0.0003, 0.0007)
        assert isclose(fe415.fs(x), y)

    # Verify stress for strain between 0.95 and 0.975 times fd
    def test_rebar14(self):
        fe415 = RebarHYSD('Fe 415', 415)
        Es = fe415.Es
        x = 0.95 * fe415.fd / Es + 0.0007 +0.00005
        y = get_fs(fe415.fd, 0.00005, 0.95, 0.975, 0.0007, 0.001)
        assert isclose(fe415.fs(x), y)

    # Verify stress for strain between 0.975 and 1.0 times fd
    def test_rebar15(self):
        fe415 = RebarHYSD('Fe 415', 415)
        Es = fe415.Es
        x = 0.975 * fe415.fd / Es + 0.001 +0.00005
        y = get_fs(fe415.fd, 0.00005, 0.975, 1.0, 0.001, 0.002)
        assert isclose(fe415.fs(x), y)

    def test_rebar16(self):
        ms = RebarMS('MS', 250)
        es = np.array([0.001, 0.002])
        fs = ms.fs(es)
        a = fs == np.array([200, 250/1.15])
        assert a.all()

    def test_rebar17(self):
        fe415 = RebarHYSD('Fe 415', 415)
        es = np.array([0.001, 0.003805])
        fs = fe415.fs(es)
        a = fs == np.array([200, 415/1.15])
        assert a.all()

