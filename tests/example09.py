# Example 08

import numpy as np

from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.rebar import RebarHYSD, LateralTie, RebarLayer, RebarGroup
from rcdesign.is456.section import RectColumnSection

b = 230
D = 450
csb = LSMStressBlock("LSM Compression")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)
L1 = RebarLayer(fe415, [16, 16, 16], 50)
L2 = RebarLayer(fe415, [16, 16, 16], -50)
long_st = RebarGroup([L1, L2])
lat_ties = LateralTie(fe415, 8, 150)
colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)

k1 = np.arange(0, 1, 0.05)
k2 = np.arange(1, 10, 1)
k3 = np.arange(10, 101, 10)
k = np.concatenate([k1, k2, k3])
k[0] = 1e-12
print(colsec)
hdr = f"{'k':>6} {'Pu (kN)':>10} {'Mu (kNm)':>10}"
print(f"{hdr}\n{'-'*len(hdr)}")
for kk in k:
    xu = kk * D
    Pu, Mu = colsec.C_M(xu)
    e = Mu / Pu
    e1 = e - (kk - 0.5) * D
    print(f"{kk:6.2f} {Pu/1e3:10.2f} {Pu * e1 / 1e6:10.2f}")
print(f"{'-'*len(hdr)}")
