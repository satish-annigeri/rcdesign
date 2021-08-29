import numpy as np
from numpy import sign
from scipy.optimize import fsolve, brentq
from typing import Callable

def func(x: float, *args) -> float:
    # return a*x**2 + c*x - 4
#     return x**3 - 10*x**2 + 5
    return args[0]**3 + args[1]*x**2 + args[2]*x + args[3]

def rootsearch(func: Callable, xstart: float, xstop: float, numint: int, *args):
    dx = (xstop - xstart) / (numint)

    x1 = xstart
    y1 = func(x1, *args)
    print('RS:', x1, y1)
    while x1 < xstop:
        x2 = x1 + dx
        y2 = func(x2, *args)
        print('RS', x2, y2)
        if sign(y1) != sign(y2):
            return (x1, x2)
        else:
            x1, y1 = x2, y2
    return (None, None)


if __name__ == '__main__':
    x1, x2 = rootsearch(func, 0, 3, 6, 1, -10, 0, 5)
    print('Bracket for roots:', x1, x2)
    if x1:
        x = fsolve(func, 2, args=(1, -10, 0, 5))
        print('fsolve()', x[0])
        x = brentq(func, x1, x2, args=(1, -10, 0, 5))
        print('brentq()', x)

