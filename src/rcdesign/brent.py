from typing import Callable
from math import isclose


def bracket(
    f: Callable, xa: float, xb: float, *args, intervals: int = 10, **kwargs
) -> tuple[float | None, float | None]:
    """
    Bracket the root of the function f in the interval [xa, xb].
    """
    fa = f(xa, *args, **kwargs)
    if isclose(fa, 0, abs_tol=1e-9):
        return xa, xa
    fb = f(xb, *args, **kwargs)
    if isclose(fb, 0, abs_tol=1e-9):
        return xb, xb

    dx = (xb - xa) / intervals
    x1 = xa
    f1 = fa
    for i in range(intervals):
        x2 = xa + (i + 1) * dx
        f2 = f(x2, *args, **kwargs)

        if f1 * f2 <= 0:
            return x1, x2
        x1, f1 = x2, f2
    return None, None


def search(
    f: Callable,
    xa: float,
    xb: float,
    *args,
    intervals: int = 10,
    max_intervals: int = 100,
    **kwargs,
) -> tuple[float | None, float | None]:
    while intervals < max_intervals:
        x1, x2 = bracket(f, xa, xb, *args, intervals=intervals, **kwargs)
        if x1 and x2:
            return x1, x2
        else:
            intervals *= 2
    return None, None


def bisection(
    f: Callable,
    xa: float,
    xb: float,
    *args,
    abs_tol: float = 1e-6,
    maxiter: int = 30,
    **kwargs,
) -> float:
    fa = f(xa, *args, **kwargs)
    if isclose(fa, 0, abs_tol=abs_tol):
        return xa

    fb = f(xb, *args, **kwargs)
    if isclose(fb, 0, abs_tol=abs_tol):
        return xb

    if fa * fb > 0:
        print(xa, fa, "|", xb, fb)
        raise ValueError("Function values at the endpoints must have opposite signs.")

    xc = (xa + xb) * 0.5
    fc = f(xc, *args, **kwargs)
    if isclose(fc, 0, abs_tol=abs_tol):
        return xc

    for i in range(1, maxiter + 1):
        if fa * fc < 0:
            xb, fb = xc, fc
        else:
            xa, fa = xc, fc
        xc = (xa + xb) * 0.5
        fc = f(xc, *args, **kwargs)
        if isclose(fc, 0, abs_tol=abs_tol):
            return xc
    raise RuntimeError("Maximum number of iterations exceeded.")


def brent(
    f: Callable,
    xa: float,
    xb: float,
    *args,
    abs_tol: float = 1e-6,
    maxiter: int = 30,
    **kwargs,
) -> float:
    x1 = xa
    f1 = f(x1, *args, **kwargs)
    if isclose(f1, 0, abs_tol=abs_tol):
        return x1
    x2 = xb
    f2 = f(x2, *args, **kwargs)
    if isclose(f2, 0, abs_tol=abs_tol):
        return x2

    if f1 * f2 > 0:
        print(x1, f1, "|", x2, f2)
        raise ValueError("Function values at the endpoints must have opposite signs.")

    x3 = (xa + xb) * 0.5

    for i in range(maxiter):
        f3 = f(x3, *args, **kwargs)
        if isclose(f3, 0, abs_tol=abs_tol):
            return x3
        # Tighten the bracket
        if f1 * f3 < 0:
            xb = x3
        else:
            xa = x3
        if (xb - xa) < abs_tol * max(abs(xb), 1.0):
            return (xa + xb) * 0.5

        # Try quadratic interpolation
        denom = (f2 - f1) * (f3 - f1) * (f2 - f3)
        numer = (
            x3 * (f1 - f2) * (f2 - f3 + f1) + f2 * x1 * (f2 - f3) + f1 * x2 * (f3 - f1)
        )
        # If division by zero, push x out of bounds
        try:
            dx = f3 * numer / denom
        except ZeroDivisionError:
            dx = xb - xa
        x = x3 + dx
        # If intersection goes out of bounds, use bisection
        if (xb - x) * (x - xa) < 0:
            dx = (xb - xa) * 0.5
            x = xa + dx
        # Let x3 <- x and choose new x1 and x2 so that x1 < x3 < x2
        if x < x3:
            x2 = x3
            f2 = f3
        else:
            x1 = x3
            f1 = f3
        x3 = x
    raise RuntimeError("Maximum number of iterations exceeded.")


if __name__ == "__main__":

    def f1(x: float, a: float, b: float, c: float) -> float:
        return a * x**2 + b * x + c

    def f2(x: float, a: float, b: float, c: float) -> float:
        return x**3 + a * x**2 + b * x + c

    a = 1
    b = -3
    c = 2
    xa, xb = search(f1, 0.5, 2.5, a, b, c)
    if xa and xb:
        print("Interval:", xa, xb)
        x = bisection(f1, xa, xb, a, b, c, abs_tol=1e-8, maxiter=40)
        print("Bisection Method:", f"{x:20.16f}, {f1(x, a, b, c):24.16g}")

        x = brent(f1, xa, xb, a, b, c, abs_tol=1e-8)
        print("  Brent's Method:", f"{x:20.16f}, {f1(x, a, b, c):24.16g}")
    else:
        print("No bracket found.")

    xa, xb = bracket(f1, 0.5, 1.0, a, b, c)
    print(xa, xb)

    x = bisection(f2, -10, 10, a, b, c, abs_tol=1e-8, maxiter=10)
    print(x, f2(x, a, b, c))
