# import numpy as np
from math import pi, ceil
from numpy import sign

# from scipy.optimize import brentq
from typing import Callable


def underline(s: str, ch: str = "-") -> str:
    """Return a string of characters, ``-`` by cefault, equal in length to a given string ``s``

    Args:
        s (str): String whose length is used to determine the length of the underline
        ch (str): Character to be used as the underline character (default: ``-``)
    Returns:
        str: String of characters ``ch``, equal in length to ``s``"""
    return ch[0] * len(s)


def header(s: str, ch: str = "-") -> str:
    """Return a string with an underline of ``ch`` characters

    Args:
        s (str): String which is to be underlined
        ch (str): Character to be used as the underline character (default: ``-``)
    Returns:
        str: String with the given input string ``s`` with an underline of ``ch`` characters."""
    return s + "\n" + underline(s, ch)


def rootsearch(func: Callable, xstart: float, xstop: float, numint: int, *args):
    """Search for values bracketing the roots of the function ``func`` between a given range of values
    by dividing the range into ``numint`` number of equal intervals.

    Args:
        func (Callable): Function whose root is to be determined
        xstart (float): Start value of the range to search
        xstop (float): End value of the range to search
        numint (int) Number of equal intervals into which the range is to be divided
        *args (tuple): Arguments to be passed on to the function ``func``
    Returns:
        tuple: Start and end values bracketing a root, else None, None
            - (``x1``, ``x2``) bracketing the root, if they can be determined, else (None, None)"""
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
    """Returns a floating point number which is a multiple of a given number and toward the ceiling
    compared to a given number ``x``

    Args:
        x (float): Reference number
        multipleof (float): The number whose multiple we wish to be returned (default: 1.0)
    Returns:
        float: A multiple of ``multipleof`` that is toward the ceiling compared to ``x``.
        Similar to the CEILING() function in Microsoft Excel"""
    i = x // multipleof
    if (x - i * multipleof) > 0:
        i += 1
    return i * multipleof


def floor(x: float, multipleof: float = 1.0):
    """Returns a floating point number which is a multiple of a given number and toward the floor
    compared to a given number ``x``

    Args:
        x (float): Reference number
        multipleof (float): The number whose multiple we wish to be returned (default: 1.0)
    Returns:
        float: A multiple of ``multipleof`` that is toward the floor compared to ``x``.
        Similar to the FLOOR() function in Microsoft Excel"""
    i = x // multipleof
    return i * multipleof


def bar_area(dia: float) -> float:
    """Returns the cross section area of one circular bar of a given diameter

    Args:
        dia (float): Diameter of circular bar
    Returns:
        float: Cross section area of one circular bar of diameter ``dia``"""
    return pi / 4 * dia**2


def num_bars(ast: float, dia: float) -> int:
    """Calculate the integer number of circular bars required to provide cross section area greater than or equal
    to a required cross section area

    Args:
        ast (float): Required cross section area
        dia (float): Diameter of circular bars to be used to provide the required cross section area
    Returns:
        int: Number of circular bars required to provide a cross section area equal to or greater than
        ``ast`` using circular bars of diameter ``dia``"""
    return int(ceil(ast / bar_area(dia)))


def deg2rad(deg: float) -> float:
    """Convert angle in degrees to radians

    Args:
        deg (float): Angle in degrees
    Returns:
        float: Angle in radians"""
    return deg * pi / 180


if __name__ == "__main__":

    def func(x: float, *args: float) -> float:
        # return a*x**2 + c*x - 4
        # return x**3 - 10*x**2 + 5
        return args[0] ** 3 + args[1] * x**2 + args[2] * x + args[3]

    print(rootsearch(func, 0, 10, 20, 1, -10, 0, 5))
