from rcdesign.utils import func, rootsearch, ceiling, floor

def test_rootsearch():
    x1, x2 = rootsearch(func, 0, 3, 6, 1, -10, 0, 5)
    assert (x1 == 0.5) and (x2 == 1.0)

def test_ceiling01():
    assert ceiling(1.21, 0.25) == 1.25

def test_ceiling02():
    assert ceiling(1.21) == 2.0

def test_ceiling03():
    assert ceiling(21.21, 25) == 25.0

def test_ceiling04():
    assert ceiling(1.213, 0.005) == 1.215

def test_floor01():
    assert floor(1.21) == 1.0

def test_floor02():
    assert floor(1.26, 0.25) == 1.25

def test_floor03():
    assert floor(105.21, 25) == 100.0