from math import isclose, pi, ceil

from rcdesign.utils import rootsearch, ceiling, floor, underline, header, bar_area, num_bars


def func(x: float, *args: float) -> float:
    # return a*x**2 + c*x - 4
    # return x**3 - 10*x**2 + 5
    return args[0] ** 3 + args[1] * x**2 + args[2] * x + args[3]


def test_rootsearch01():
    x1, x2 = rootsearch(func, 0, 3, 6, 1, -10, 0, 5)
    assert (x1 == 0.5) and (x2 == 1.0)


def test_rootsearch02():
    x1, x2 = rootsearch(func, 1, 2, 4, 1, -10, 0, 5)
    assert (x1 is None) and (x2 is None)


def test_ceiling01():
    assert ceiling(1.21, 0.25) == 1.25


def test_ceiling02():
    assert ceiling(1.21) == 2.0


def test_ceiling03():
    assert ceiling(21.21, 25) == 25.0


def test_ceiling04():
    assert ceiling(1.213, 0.005) == 1.215


def test_ceiling05():
    assert ceiling(125.0, 25) == 125.0


def test_floor01():
    assert floor(1.21) == 1.0


def test_floor02():
    assert floor(1.26, 0.25) == 1.25


def test_floor03():
    assert floor(105.21, 25) == 100.0


def test_floor04():
    assert isclose(floor(125.0, 25), 125.0)


def test_uline():
    assert underline("Satish Annigeri") == "---------------"
    assert underline("Satish Annigeri", "=") == "==============="
    assert header("Satish Annigeri") == "Satish Annigeri\n---------------"
    assert header("Satish Annigeri", "=") == "Satish Annigeri\n==============="


def test_bar_area():
    dia = 16
    assert bar_area(dia) == pi / 4 * dia**2
    Ast = 620.0
    n = int(ceil(Ast / bar_area(dia)))
    assert num_bars(Ast, dia) == n
