from math import isclose

from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.rebar import RebarHYSD, LateralTies, RebarLayer, RebarGroup
from rcdesign.is456.section import RectColumnSection


def calc_c(z1: float, z2: float, k: float) -> float:
    if (z1 < k - 1) or (z1 > k) or (z2 < k - 1) or z2 > k:
        return 0.0
    if z1 > z2:
        z1, z2 = z2, z1
    zcy = k - 3 / 7
    if z2 <= zcy:
        a1 = (z2 ** 2 - z1 ** 2) / zcy - (z2 ** 3 - z1 ** 3) / zcy ** 2 / 3
        a2 = 0.0
    elif z1 >= zcy:
        a1 = 0.0
        a2 = z2 - z1
    else:
        a1 = (zcy ** 2 - z1 ** 2) / zcy - (zcy ** 3 - z1 ** 3) / zcy ** 2 / 3
        a2 = z2 - zcy
    return a1 + a2


def calc_m(z1: float, z2: float, k: float) -> float:
    if (z1 < k - 1) or (z1 > k) or (z2 < k - 1) or z2 > k:
        return 0.0
    if z1 > z2:
        z1, z2 = z2, z1
    zcy = k - (3 / 7)
    if z2 <= zcy:
        m1 = (2 / 3 * (z2 ** 3 - z1 ** 3) / zcy) - ((z2 ** 4 - z1 ** 4) / zcy ** 2 / 4)
        m2 = 0.0
    elif z1 >= zcy:
        m1 = 0.0
        m2 = (z2 ** 2 - zcy ** 2) / 2
    else:
        m1 = (2 / 3 / zcy * (zcy ** 3 - z1 ** 3)) - (
            (zcy ** 4 - z1 ** 4) / zcy ** 2 / 4
        )
        m2 = (z2 ** 2 - zcy ** 2) / 2
    return m1 + m2


def calc_cf(z1: float, z2: float, k: float) -> float:
    if (z1 < 0) or (z1 > k) or (z2 < 0) or z2 > k:
        return 0.0
    if z1 > z2:
        z1, z2 = z2, z1
    zcy = 4 / 7 * k
    if z2 <= zcy:
        a1 = (z2 ** 2 - z1 ** 2) / zcy - (z2 ** 3 - z1 ** 3) / zcy ** 2 / 3
        a2 = 0.0
    elif z1 >= zcy:
        a1 = 0.0
        a2 = z2 - z1
    else:
        a1 = (zcy ** 2 - z1 ** 2) / zcy - (zcy ** 3 - z1 ** 3) / zcy ** 2 / 3
        a2 = z2 - zcy
    return a1 + a2


def calc_mf(z1: float, z2: float, k: float) -> float:
    if (z1 < 0) or (z1 > k) or (z2 < 0) or z2 > k:
        return 0.0
    if z1 > z2:
        z1, z2 = z2, z1
    zcy = 4 / 7 * k
    if z2 <= zcy:
        m1 = (2 / 3 * (z2 ** 3 - z1 ** 3) / zcy) - ((z2 ** 4 - z1 ** 4) / zcy ** 2 / 4)
        m2 = 0.0
    elif z1 >= zcy:
        m1 = 0.0
        m2 = (z2 ** 2 - zcy ** 2) / 2
    else:
        m1 = (2 / 3 / zcy * (zcy ** 3 - z1 ** 3)) - (
            (zcy ** 4 - z1 ** 4) / zcy ** 2 / 4
        )
        m2 = (z2 ** 2 - zcy ** 2) / 2
    return m1 + m2


if __name__ == "__main__":
    b = 230
    D = 450
    csb = LSMStressBlock("LSM Compression")
    m20 = Concrete("M20", 20)
    fe415 = RebarHYSD("Fe 415", 415)
    L1 = RebarLayer(fe415, [16, 16, 16], 50)
    L2 = RebarLayer(fe415, [16, 16], D / 2)
    L3 = RebarLayer(fe415, [16, 16, 16], -50)
    long_st = RebarGroup([L1, L2, L3])
    lat_ties = LateralTies(fe415, 8, 150)
    colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
    xu = 900
    k = xu / D  # k = 2 / 3
    print(colsec.report(xu))
