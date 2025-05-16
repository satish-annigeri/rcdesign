from math import isclose

import pytest

from rcdesign.brent import search, bracket, bisection, brent


def f1(x: float, a: float, b: float, c: float) -> float:
    return a * x**2 + b * x + c


def f2(x: float, a: float, b: float, c: float) -> float:
    return x**3 + a * x**2 + b * x + c


a = 1
b = -3
c = 2


class TestBrent:
    def test_brent(self):
        x1 = -4
        x2 = -2

        x = brent(f2, x1, x2, a, b, c)
        assert isclose(f2(x, a, b, c), 0, abs_tol=1e-6)

    def test_brent_edge(self):
        x = brent(f1, 1, 3, a, b, c)  # Start of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

        x = brent(f1, 0, 1, a, b, c)  # End of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

        x = brent(f1, 0.5, 1.5, a, b, c)  # Midpoint of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

    def test_brent_exc(self):
        with pytest.raises(
            RuntimeError,
            match="Maximum number of iterations exceeded.",
        ):
            _ = brent(f2, -10, 10, a, b, c, maxiter=3)

        with pytest.raises(
            ValueError,
            match="Function values at the endpoints must have opposite signs.",
        ):
            _ = brent(f1, 4, 6, a, b, c)

    def test_bisection(self):
        x1 = -4
        x2 = -2

        x = bisection(f2, x1, x2, a, b, c)
        assert isclose(f2(x, a, b, c), 0, abs_tol=1e-6)

    def test_bisection_edge(self):
        x = bisection(f1, 1, 3, a, b, c)  # Start of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

        x = bisection(f1, 0, 1, a, b, c)  # End of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

        x = bisection(f1, 0.5, 1.5, a, b, c)  # Midpoint of interval is a root
        assert isclose(f1(x, a, b, c), 0, abs_tol=1e-6)

    def test_bisection_exc(self):
        with pytest.raises(
            RuntimeError,
            match="Maximum number of iterations exceeded.",
        ):
            _ = bisection(f2, -10, 10, a, b, c, maxiter=5)
        with pytest.raises(
            ValueError,
            match="Function values at the endpoints must have opposite signs.",
        ):
            _ = bisection(f1, 4, 6, a, b, c)

    def test_search(self):
        x1 = -10
        x2 = 10
        xa, xb = search(f1, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, 0.5, abs_tol=1e-6)
        assert isclose(xb, 1.0, abs_tol=1e-6)

        xa, xb = search(f2, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, -4.0, abs_tol=1e-6)
        assert isclose(xb, -2.0, abs_tol=1e-6)

    def test_search_noroots(self):
        x1 = 4
        x2 = 10
        xa, xb = search(f1, x1, x2, a, b, c)
        assert xa is None
        assert xb is None

    def test_bracket(self):
        x1 = 0.5
        x2 = 2.5

        xa, xb = bracket(f1, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, 0.9, abs_tol=1e-6)
        assert isclose(xb, 1.1, abs_tol=1e-6)

        x1 = -10
        x2 = 10
        xa, xb = bracket(f2, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, -4.0, abs_tol=1e-6)
        assert isclose(xb, -2.0, abs_tol=1e-6)

    def test_bracket_no_root(self):
        x1 = 4
        x2 = 10
        xa, xb = bracket(f1, x1, x2, a, b, c)
        assert xa is None
        assert xb is None

    def test_bracket_edge(self):
        x1 = 1.0
        x2 = 2.5
        xa, xb = bracket(f1, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, 1.0, abs_tol=1e-6)
        assert isclose(xb, 1.0, abs_tol=1e-6)

        x1 = 0.5
        x2 = 1.0
        xa, xb = bracket(f1, x1, x2, a, b, c)
        assert xa is not None
        assert xb is not None
        assert isclose(xa, 1.0, abs_tol=1e-6)
        assert isclose(xb, 1.0, abs_tol=1e-6)
