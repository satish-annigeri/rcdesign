# import numpy as np`
# import matplotlib.pyplot as plt
from scipy.optimize import brentq
from rcdesign.utils import rootsearch

from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups#, RebarMS
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection

from rcdesign import __version__

m20 = Concrete('M20', 20, ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035))
# print(m20.fd, m20.fc(1), m20.area(0, 1))

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

sec1 = RectBeamSection(230, 450, m20, t_st, c_st, fe415, 25)
# print(sec1)
xu = 136.210193097794
print('Compression:', sec1.C(xu, 0.0035))
print('    Tension:', sec1.T(xu, 0.0035))
print(sec1.C_T(xu, 0.0035))
x1, x2 = rootsearch(sec1.C_T, 50, 400, 10, sec1.conc.ecu)
print(x1, x2)
xu = brentq(sec1.C_T, x1, x2, args=(sec1.conc.ecu,), xtol=1e-4)
print(xu, sec1.C_T(xu, sec1.conc.ecu))
sec1.report(xu, sec1.conc.ecu)

concsb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
# print(concsb.ecy)
conc = Concrete('M20', 20, concsb)
t1 = RebarLayer(35, [16, 16, 16])
t2 = RebarLayer(70, [16, 16])
t_st = RebarGroup(RebarHYSD('Fe 415', 415), [t1, t2])
c_st = RebarGroup(RebarHYSD('Fe 415', 415), [c1])
sec_st = RebarHYSD('Fe415', 415)
shear_steel = Stirrups(RebarHYSD('Fe 415', 415), 2, 8, 90, 125)
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)
# shear_steel.nlegs = 4
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)
# shear_steel.bar_dia = 10
# print(shear_steel.nlegs, shear_steel.bar_dia, shear_steel.Asv)

tsec = FlangedBeamSection(230, 450, 1000, 150, conc, t_st, None, shear_steel, 25)

# xu = 50.16570748
# xu = 150
# print(f"xu = {xu} C = {tsec.C(xu, 0.0035)}")
# print(f"xu = {xu} T = {tsec.T(xu, 0.0035)}")

# xumax = tsec.xumax(tsec.eff_d())
# xumax = 190
# print('xumax =', xumax)
# print(f"xu = {xumax} C = {tsec.C(xumax, 0.0035)} Mr = {tsec.Mr(xumax, 0.0035)}")

# if xumax > tsec.Df:
#     print(f"xu = {xumax} Mr = {tsec.Mr(xumax, 0.0035)}")

# x = np.linspace(5, xumax, 5)
# for xx in x:
#     print(f"xu = {xx:8.2f} Mr = {tsec.Mr(xx, 0.0035)/1e6:8.2f}")

xu, Mu = sec1.analyse(0.0035)
print('xxx', xu, Mu)
Vu = tsec.Vu()
print(f"Vu = {Vu/1e3:.2f}")
Vu = 190e3
sv = tsec.sv(Vu, 2, 8)
print(f"Vu = {Vu/1e3:.2f} sv = {sv:.2f}")
print(f"Vu = {tsec.Vu(2, 10, 300)/1e3:.2f}")
