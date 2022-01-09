# Example 08

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
L2 = RebarLayer(fe415, [16, 16], D / 2)
L3 = RebarLayer(fe415, [16, 16, 16], -50)
long_st = RebarGroup([L1, L2, L3])
lat_ties = LateralTie(fe415, 8, 150)
colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
xu = 900
k = xu / D  # k = 2 / 3
print(colsec.report(xu))
