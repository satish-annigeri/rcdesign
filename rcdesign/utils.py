# import numpy as np
from math import pi, ceil
from numpy import sign

# from scipy.optimize import brentq
from typing import Callable


def underline(s: str, ch: str = "-") -> str:
    return ch * len(s)


def header(s: str, ch: str = "-") -> str:
    return s + "\n" + underline(s, ch)


def func(x: float, *args: float) -> float:
    # return a*x**2 + c*x - 4
    # return x**3 - 10*x**2 + 5
    return args[0] ** 3 + args[1] * x**2 + args[2] * x + args[3]


def rootsearch(func: Callable, xstart: float, xstop: float, numint: int, *args):
    dx = (xstop - xstart) / (numint)
    x1 = xstart
    y1 = func(x1, *args)
    while x1 < xstop:
        x2 = x1 + dx
        y2 = func(x2, *args)
        if sign(y1) != sign(y2):
            return (x1, x2)
        else:
            x1, y1 = x2, y2
    return (None, None)


def ceiling(x: float, multipleof: float = 1.0):
    i = x // multipleof
    if (x - i * multipleof) > 0:
        i += 1
    return i * multipleof


def floor(x: float, multipleof: float = 1.0):
    i = x // multipleof
    return i * multipleof


def bar_area(dia: float) -> float:
    return pi / 4 * dia ** 2


def num_bars(ast: float, dia: float) -> int:
    return int(ceil(ast / bar_area(dia)))


def deg2rad(deg: float) -> float:
    return deg * pi / 180
