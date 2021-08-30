import numpy as np
# import matplotlib.pyplot as plt
from scipy.optimize import brentq

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarMS, RebarHYSD, RebarLayer, RebarGroup
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection
from rcdesign.utils import rootsearch

m20 = Concrete('M20', 20, ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035))
# print(m20.fd, m20._area(0, 1))

# ms = RebarMS('MS 250', 250)
# print(ms)

fe415 = RebarHYSD('Fe 415', 415)
# print(fe415)

# fe500 = RebarHYSD('Fe 500', 500)
# print(fe500)

t1 = RebarLayer(35, [16, 16, 16])
t2 = RebarLayer(70, [16, 16])
c1 = RebarLayer(35, [16, 16])
t_st = RebarGroup(fe415, [t1, t2])
c_st = RebarGroup(fe415, [c1])

# sec1 = RectBeamSection(230, 450, m20, t_st, c_st, fe415, 25)
# # print(sec1)
# xu = 136.210193097794
# print('Compression:', sec1.C(xu, 0.0035))
# print('    Tension:', sec1.T(xu, 0.0035))
# print(sec1.C_T(xu, 0.0035))
# x1, x2 = rootsearch(sec1.C_T, 50, 400, 10, sec1.conc.ecu)
# print(x1, x2)
# xu = brentq(sec1.C_T, x1, x2, args=(sec1.conc.ecu,), xtol=1e-4)
# print(xu, sec1.C_T(xu, sec1.conc.ecu))
# sec1.report(xu, sec1.conc.ecu)

bw = 230
D = 450
bf = 1000
Df = 150
tsec = FlangedBeamSection(bw, D, bf, Df, m20, t_st, c_st, fe415, 25)
print(tsec.C(160, 0.0035))