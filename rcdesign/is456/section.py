"""Class to represent reinforced concrete cross sections"""

from enum import Enum
# from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod
from scipy.optimize import brentq

# import numpy as np
# from numpy import pi

from .material.concrete import ConcreteStressBlock, Concrete
from .material.rebar import Rebar, RebarMS, RebarHYSD, RebarLayer, RebarGroup, ShearReinforcement #, Stirrups, BentupBars
from rcdesign.utils import floor

from ..utils import rootsearch

# DesignForce class

class DesignForceType(Enum):
    BEAM = 1
    COLUMN = 2
    SLAB = 3
    SHEARWALL = 4


class Section(ABC): # pragma: no cover
    def __init__(self, design_force_type, clear_cover):
        self.design_force_type = design_force_type
        self.clear_cover = clear_cover

    @abstractmethod
    def C(self, xu: float, ecmax: float):
        pass
    # @abstractmethod
    # def design(self):
    #     pass

    # @abstractmethod
    # def analyse(self, ecu: float):
    #     pass

# RectSection class to repersent a rectangular section

class RectBeamSection(Section):
    def __init__(self, b: float, D: float, conc: Concrete, t_steel: RebarGroup, c_steel: RebarGroup, shear_steel: ShearReinforcement, clear_cover: float):
        super().__init__(DesignForceType.BEAM, clear_cover)
        self.b = b
        self.D = D
        self.conc = conc
        self.t_steel = t_steel
        self.c_steel = c_steel
        self.shear_steel = shear_steel

    def xumax(self, d: float=1):
        es_min = self.t_steel.rebar.es_min()
        return 0.0035 / (es_min + 0.0035) * d

    def mulim(self, d: float):
        xumax = self.xumax() * d
        return (17/21) * self.conc.fd * self.b * xumax * (d - (99/238)*xumax)

    def C(self, xu: float, ecu: float):
        C1 = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        M1 = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.b

        if self.c_steel:
            C2, M2 = self.c_steel.force_compression(xu, self.conc, ecu)
        else:
            C2 = 0.0  # in case there is no compression steel
            M2 = 0.0
        C, M = C1 + C2, M1 + M2
        return C, M

    def T(self, xu: float, ecu: float):
        _T, _M = self.t_steel.force_tension(xu, self.D - xu, ecu)
        return _T, _M

    def C_T(self, x: float, ecu: float):
        C, _ = self.C(x, ecu)
        T, _ = self.T(x, ecu)
        return C - T

    def xu(self, ecu: float):
        x1, x2 = rootsearch(self.C_T, self.t_steel.layers[0].dc, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def Mu(self, xu: float, ecu: float):
        # Assuming tension steel to produce an equal tension force as C
        C, M = self.C(xu, ecu)
        return M + C * (self.eff_d() - xu)

    def analyse(self, ecu: float):
        xu = self.xu(ecu)
        Mu = self.Mu(xu, ecu)
        print('***', xu, Mu)
        return xu, Mu

    def pt(self):
        d = self.eff_d()
        ast = self.t_steel.area()
        return ast / (self.b * d) * 100

    def tauc(self):
        return self.conc.tauc(self.pt())

    def __repr__(self): # pragma: no cover
        return f"Size: {self.b} x {self.D}\nTension Steel: {self.t_steel}\nCompression Steel: {self.c_steel}"

    def report(self, xu: float, ecu: float): # pragma: no cover
        print(f"Rectangular Beam Section {self.b}x{self.D}")
        print()
        C = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        Mc = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.b
        print(f"{' ':54}{'C':>8} {'M':>8}")
        print(f"{'Concrete in Compression':54}{C/1e3:8.2f} {Mc/1e6:8.2f}")
        print("Compression Reinforcement")
        print(f"{'dc':>4} {'Area':>8} {'x':>8} {'Strain':>12} {'f_sc':>8} {'f_cc':>8} {'C':>8} {'M':>8}")
        for layer in self.c_steel.layers:
            x = xu - layer.dc
            esc = ecu / xu * x
            fsc = self.c_steel.rebar.fs(esc)
            fcc = self.conc.fc(esc)
            Fsc = layer.area() * (fsc - fcc)
            C += Fsc
            Msc = Fsc * x
            Mc += Msc
            print(f"{layer.dc:4.0f} {layer.area():8.2f} {x:8.2f} {esc:12.4e} {fsc:8.2f} {fcc:8.2f} {Fsc/1e3:8.2f} {Msc/1e6:8.2f}")
        print(f"{' '*54}{C/1e3:8.2f} {Mc/1e6:8.2f}")
        print("Tension Reinforcement")
        T = 0
        Mt = 0
        print(f"{'dc':>4} {'Area':>8} {'x':>8} {'Strain':>12} {'f_st':>8} {' ':8} {'T':>8} {'M':>8}")
        for layer in self.t_steel.layers:
            x = self.D - xu - layer.dc
            est = ecu / xu * x
            fst = self.t_steel.rebar.fs(est)
            Fst = layer.area() * fst
            T += Fst
            Mst = Fst * x
            Mt += Mst
            print(f"{layer.dc:4.0f} {layer.area():8.2f} {x:8.2f} {est:12.4e} {fst:8.2f} {' ':8} {Fst/1e3:8.2f} {Mst/1e6:8.2f}")
        print(f"{' '*54}{T/1e3:8.2f} {Mt/1e6:8.2f}")
        M = Mc + Mt
        print('-'*71)
        print(f"{' '*54}{(C - T)/1e3:8.4f} {M/1e6:8.2f}")

    # def design(self, Mu: float, Vu: float=0, Tu: float=0):
    #     d = self.D - self.clear_cover - 25.0
    #     mulim = self.mulim(d) * self.conc.fck * self.b * d**2
    #     if abs(Mu) > mulim:
    #         print(f'Doubly reinforced section (Mu,lim = {mulim / 1e6}')
    #     else:
    #         print(f'Singly reinforced section (Mu,lim = {mulim / 1e6})')
    
    def eff_d(self):
        return self.D - self.t_steel._dc()

    def Vu(self, nlegs: int=0, bar_dia: int=0, sv: float=0):
        if nlegs > 0:
            self.nlegs = nlegs
        if bar_dia > 0:
            self.bar_dia = bar_dia
        if sv > 0:
            self.shear_steel._sv = sv
        pt = self.t_steel.area() * 100 / (self.b * self.eff_d())
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * self.eff_d()
        Vus = self.shear_steel.rebar.fd * self.shear_steel.Asv * self.eff_d() / self.shear_steel._sv
        return Vuc + Vus

    def sv(self, Vu: float, nlegs: int, bar_dia: int, mof: float=25):
        self.shear_steel.nlegs = nlegs
        self.shear_steel.bar_dia = bar_dia

        pt = self.t_steel.area() * 100 / (self.b * self.eff_d())
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * self.eff_d()

        Vus = Vu - Vuc
        self._sv = self.shear_steel.rebar.fd * self.shear_steel._Asv * self.eff_d() / Vus
        self._sv = floor(self._sv, mof)
        return self._sv
    

"""Class to repersent flanged section"""
@dataclass
class FlangedBeamSection(RectBeamSection):
    def __init__(self, bw: float, D: float, bf: float, Df: float, conc: Concrete, t_steel: RebarGroup, c_steel: RebarGroup, shear_steel: Rebar, clear_cover: float):
        super().__init__(bw, D, conc, t_steel, c_steel, shear_steel, clear_cover)
        bw: float
        # D: float
        self.bf = bf
        self.Df = Df

    @property
    def bw(self):
        return self.b

    def C(self, xu: float, ecu: float):
        # Compression force and moment due to concrete of web
        C1 = self.conc.area(0, 1, self.conc.fd) * xu * self.bw
        M1 = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.bw
        # print('Flanged - Web:', C1, M1)
        # Compression force and moment due to compression reinforcement bars
        if self.c_steel:
            C2, M2 = self.c_steel.force_compression(xu, self.conc, ecu)
        else:
            # print('No compression steel')
            C2 = 0.0
            M2 = 0.0
        # print('Flanged - Compression steel:', C2, M2)
        # Compression force and moment due to concrete of flange
        df = xu if xu <= self.Df else self.Df
        x1 = xu - df
        C3 = self.conc.area(x1/xu, 1, self.conc.fd) * xu * (self.bf - self.bw)
        M3 = self.conc.moment(x1/xu, 1, self.conc.fd) * df**2 * (self.bf - self.bw)
        # print('Flanged - Flange', C3, M3)
        C = C1 + C2 + C3
        M = M1 + M2 + M3
        # print(C1, C2, C3, C)
        return C, M

    def T(self, xu: float, ecu: float):
        _T, _M = self.t_steel.force_tension(xu, self.D - xu, ecu)
        return _T, _M

    def Mr(self, xu: float, ecu: float):
        # Assuming tension steel to produce an equal tension force as C
        C, M = self.C(xu, ecu)
        return M + C * (self.eff_d() - xu)

    def __repr__(self): # pragma: no cover
        s = f'Flanged Beam Section {self.bw}x{self.D} {self.bf}x{self.Df}\n'
        s += self.conc.__repr__() + '\n'
        s += f"{self.c_steel.layers[0]}\n"
        return s

    def analyse(self, xu: float, ecmax: float):
        pass

    def design(self):
        pass


if __name__ == '__main__':
    m20 = Concrete('M20', 20, ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035))
    # print(m20.fd, m20._area(0, 1))

    ms = RebarMS('MS 250', 250)
    # print(ms)

    fe415 = RebarHYSD('Fe 415', 415)
    # print(fe415)

    fe500 = RebarHYSD('Fe 500', 500)
    print(fe500)

    t1 = RebarLayer(35, [16, 16, 16])
    t2 = RebarLayer(70, [16, 16])
    c1 = RebarLayer(35, [16, 16])
    t_st = RebarGroup(fe415, [t1, t2])
    c_st = RebarGroup(fe415, [c1])

    # sec1 = RectBeamSection(230, 450, m20, t_st, c_st, fe415, 25)
    # print(sec1)
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
