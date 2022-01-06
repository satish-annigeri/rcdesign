from math import isclose

from rcdesign.utils import func, rootsearch, ceiling, floor, underline, header


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
