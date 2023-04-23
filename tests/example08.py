# Example 08

from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.rebar import RebarHYSD, LateralTie, RebarLayer, RebarGroup
from rcdesign.is456.section import RectColumnSection

b = 230
D = 600
csb = LSMStressBlock("LSM Compression")
m20 = Concrete("M20", 20)
fe415 = RebarHYSD("Fe 415", 415)
fe500 = RebarHYSD("Fe 500", 500)
L1 = RebarLayer(fe500, [16, 16, 16], 50)
# L2 = RebarLayer(fe500, [16, 16], D / 2)
L3 = RebarLayer(fe500, [16, 16, 16], -50)
long_st = RebarGroup([L1, L3])
lat_ties = LateralTie(fe500, 8, 230)
colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 42)
xu = 240
print(colsec.report(xu))
print(xu / D, colsec.C_M(xu))
