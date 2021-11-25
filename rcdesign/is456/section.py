"""Class to represent reinforced concrete cross sections"""

from math import isclose
from enum import Enum
from typing import Tuple, List, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
from scipy.optimize import brentq


from .material.concrete import Concrete
from .material.rebar import Rebar, RebarGroup, ShearRebarGroup, ShearReinforcement
from rcdesign.utils import floor

from ..utils import rootsearch


# DesignForce class


class DesignForceType(Enum):
    BEAM = 1
    COLUMN = 2
    SLAB = 3
    SHEARWALL = 4


class Section(ABC):  # pragma: no cover
    def __init__(
        self,
        design_force_type: DesignForceType,
        conc: Concrete,
        long_steel: RebarGroup,
        clear_cover: float,
    ):
        self.design_force_type = design_force_type
        self.conc = conc
        self.long_steel = long_steel
        self.clear_cover = clear_cover

    @abstractmethod
    def C(self, xu: float, ecmax: float):
        pass


"""Class to repersent a rectangular beam section"""


class RectBeamSection(Section):
    def __init__(
        self,
        b: float,
        D: float,
        conc: Concrete,
        long_steel: RebarGroup,
        shear_steel: ShearRebarGroup,
        clear_cover: float,
    ):
        super().__init__(DesignForceType.BEAM, conc, long_steel, clear_cover)
        self.b = b
        self.D = D

        self.shear_steel = shear_steel
        self.calc_xc()

    def calc_xc(self) -> None:
        self.long_steel.calc_xc(self.D)
        return None

    def adjust_x(self, xu: float) -> None:
        for layer in self.long_steel.layers:
            # Calculate _xc from _dc
            if layer._dc < 0:
                layer._xc = self.D + layer._dc
            else:
                layer._xc = layer._dc
            # Decide type of stress
            if layer._xc < xu:
                layer.stress_type = "compression"
            elif layer._xc > xu:
                layer.stress_type = "tension"
            elif layer._xc == xu:
                layer.stress_type = "neutral"

    def xumax(self, d: float = 1) -> float:
        es_min = self.long_steel.rebar.es_min()
        return 0.0035 / (es_min + 0.0035) * d

    def mulim(self, d: float) -> float:
        xumax = self.xumax() * d
        return (17 / 21) * self.conc.fd * self.b * xumax * (d - (99 / 238) * xumax)

    def C(self, xu: float, ecmax: float) -> Tuple[float, float]:
        C, _, M, _ = self.force_moment(xu, ecmax)
        return C, M

    def force_moment(
        self, xu: float, ecmax: float
    ) -> Tuple[float, float, float, float]:
        self.adjust_x(xu)
        Fc = Mc = Ft = Mt = 0.0
        area = self.conc.area(0, 1, self.conc.fd)
        moment = self.conc.moment(0, 1, self.conc.fd)
        Fcc = area * xu * self.b
        Mcc = moment * xu ** 2 * self.b
        Fc += Fcc
        Mc += Mcc
        Fsc = Msc = Fst = Mst = 0.0
        Fsc, Msc, Fst, Mst = self.long_steel.force_moment(xu, self.conc, ecmax)
        Fc += Fsc
        Mc += Msc
        Ft += Fst
        Mt += Mst
        return Fc, Ft, Mc, Mt

    def T(self, xu: float, ecmax: float) -> Tuple[float, float]:
        _, _T, _, _M = self.force_moment(xu, ecmax)
        return _T, _M

    def C_T(self, x: float, ecmax: float) -> float:
        self.adjust_x(x)
        C, T, _, _ = self.force_moment(x, ecmax)
        return C - T

    def xu(self, ecmax: float) -> float:
        dc_max = 10

        x1, x2 = rootsearch(self.C_T, dc_max, self.D, 10, ecmax)
        x = brentq(self.C_T, x1, x2, args=(ecmax,))
        return x

    def Mu(self, xu: float, ecmax: float) -> float:
        # Assuming area of tension steel to such as to produce a tension force equal to C
        C, M = self.C(xu, ecmax)
        return M + C * (self.eff_d(xu) - xu)

    def analyse(self, ecmax: float) -> Tuple[float, float]:
        xu = self.xu(ecmax)
        Mu = self.Mu(xu, ecmax)
        return xu, Mu

    def tauc(self, xu: float) -> float:
        return self.conc.tauc(self.pt(xu))

    def __repr__(self) -> str:
        ecmax = self.conc.stress_block.ecu
        xu = self.xu(ecmax)
        return self.report(xu, ecmax)

    def has_compr_steel(self, xu: float) -> bool:
        for L in self.long_steel.layers:
            if L._xc < xu:
                return True
        return False

    def report(self, xu: float, ecmax: float) -> str:  # pragma: no cover
        self.adjust_x(xu)
        d = self.long_steel.report(xu, self.conc, self.long_steel.rebar, ecmax)
        s = f"RECTANGULAR BEAM SECTION: {self.b} x {self.D}\n"
        s += f"FLEXURE\nEquilibrium NA = {xu:.2f} (ec,max = {ecmax:.6f})\n"
        s += f"Concrete: {self.conc}\n"
        Fc = self.b * self.conc.area(0, 1, self.conc.fd) * xu / 1e3
        Mc = self.conc.moment(0, 1, self.conc.fd) * self.b * xu ** 2 / 1e6
        s += f"{' ':>8}{'dc':>6}{'xc':>6}{'Bars':>12}{'Area':>10}{'Stress':>8}{'x NA':>10}{'Strain':>12}"
        s += f"{'fs':>10}{'fc':>10}{'Force':>10}{'Moment':>10}\n"
        s += f"{'Concrete':>8}{'C':>42}{xu:10.2f}{ecmax:12.4e}{' ':>10}"
        s += f"{self.conc.fd:10.2f}{Fc:10.2f}{Mc:10.2f}\n"
        Ft = 0.0
        Mt = 0.0
        for L in d:
            s += f"{'Rebar':>8}{L['dc']:6}{L['xc']:6}{L['bars']:>12}{L['area']:10.2f}{L['type']:>8}"
            s += f"{abs(float(L['x'])):10.2f}{L['es']:12.4e}{L['fs']:10.2f}"
            if L["type"] == "C":
                s += f"{L['fc']:10.2f}"
                Fc += float(L["F"]) / 1e3
                Mc += float(L["M"]) / 1e6
            else:
                s += f"{' ':>10}"
                Ft += float(L["F"]) / 1e3
                Mt += float(L["M"]) / 1e6
            F = float(L["F"]) / 1e3
            M = float(L["M"]) / 1e6
            s += f"{F:10.2f}{M:10.2f}\n"
        s += f"{' ':>92}{'-'*10}{'-'*10}\n"
        s += f"{abs(Fc - Ft):102.2f}{(Mc + Mt):10.2f}\n"
        s += f"SHEAR\n{self.shear_steel}\n"
        s += f"CAPACITY\n{'Mu = ':>5}{self.Mu(xu, ecmax)/1e6:.2f} kNm\n"
        vuc, vus = self.Vu(xu)
        vu = vuc + sum(vus)
        s += f"{'Vu = ':>5}{vu/1e3:.2f} kN\n"
        return s

    def eff_d(self, xu: float) -> float:
        a = 0.0
        m = 0.0
        for L in sorted(self.long_steel.layers):
            if L._xc >= xu:
                _a = L.area
                _m = _a * L._xc
                a += _a
                m += _m
        return m / a

    def pt(self, xu: float) -> float:
        d = self.eff_d(xu)
        ast = 0.0
        for L in sorted(self.long_steel.layers):
            if L._xc > xu:
                ast += L.area
        pt = ast / (self.b * d) * 100
        # print("xxx", d, ast, pt)
        return pt

    def Vu(self, xu: float) -> Tuple[float, List[float]]:
        # print("\nstart::RectBeamSection.Vu(xu)", xu)
        pt = self.pt(xu)
        # print("stop::RectBeamSection.Vu(xu)\n")
        tauc = self.conc.tauc(pt)
        d = self.eff_d(xu)
        vuc = tauc * self.b * d
        vus = self.shear_steel.Vus(d)
        # print("===", vuc, vus)
        return vuc, vus


"""Class to repersent flanged section"""


class FlangedBeamSection(RectBeamSection):
    def __init__(
        self,
        bw: float,
        D: float,
        bf: float,
        Df: float,
        conc: Concrete,
        long_steel: RebarGroup,
        shear_steel: ShearRebarGroup,
        clear_cover: float,
    ):
        super().__init__(bw, D, conc, long_steel, shear_steel, clear_cover)
        self.bf = bf
        self.Df = Df

    @property
    def bw(self) -> float:
        return self.b

    @bw.setter
    def bw(self, _bw) -> None:
        self.b = _bw

    def Cw(self, xu: float, ecmax: float) -> Tuple[float, float]:
        area = self.conc.area(0, 1, self.conc.fd)
        moment = self.conc.moment(0, 1, self.conc.fd)

        C = area * xu * self.bw
        M = moment * xu ** 2 * self.bw
        return C, M

    def Cf(self, xu: float) -> Tuple[float, float]:
        df = xu if xu <= self.Df else self.Df
        x1 = xu - df
        area = self.conc.area(x1 / xu, 1, self.conc.fd)
        moment = self.conc.moment(x1 / xu, 1, self.conc.fd)

        C = area * xu * (self.bf - self.bw)
        M = moment * xu ** 2 * (self.bf - self.bw)
        return C, M

    def C(self, xu: float, ecmax: float) -> Tuple[float, float]:
        # Compression force and moment due to concrete of web
        C1, M1 = self.Cw(xu, ecmax)
        # Compression force and moment due to compression reinforcement bars
        if self.has_compr_steel(xu):
            C2, M2 = self.long_steel.force_compression(xu, self.conc, ecmax)
        else:
            C2 = M2 = 0.0

        # Compression force and moment due to concrete of flange
        C3, M3 = self.Cf(xu)

        # Sum it all up
        C = C1 + C2 + C3
        M = M1 + M2 + M3
        return C, M

    def Mu(self, xu: float, ecmax: float) -> float:
        d = self.eff_d(xu)
        # Based on compression force C, assuming the right amount of tension steel
        C, M = self.C(xu, ecmax)
        Mu = M + C * (d - xu)
        return Mu

    def __repr__(self) -> str:
        ecmax = self.conc.stress_block.ecu
        xu = self.xu(ecmax)
        return self.report(xu, ecmax)

    def C_T(self, x: float, ecmax: float) -> float:
        C, _ = self.C(x, ecmax)
        T, _ = self.T(x, ecmax)
        # if C and T:
        return C - T
        # else:
        #     return None

    def xu(self, ecmax: float) -> float:
        # x1, x2 = rootsearch(self.C_T, self.t_steel.layers[0].dc, self.D, 10, ecmax)
        x1, x2 = rootsearch(self.C_T, 10, self.D, 10, ecmax)
        x = brentq(self.C_T, x1, x2, args=(ecmax,))
        return x

    def analyse(self, ecmax: float) -> Tuple[float, float]:
        xu = self.xu(ecmax)
        Mu = self.Mu(xu, ecmax)
        return xu, Mu

    def report(self, xu: float, ecmax: float) -> str:  # pragma: no cover
        self.adjust_x(xu)
        d = self.long_steel.report(xu, self.conc, self.long_steel.rebar, ecmax)
        s = f"FLANGED BEAM SECTION - Web: {self.b} x {self.D}, Flange: {self.bf} x {self.Df}\n"
        s += f"FLEXURE\nEquilibrium NA = {xu:.2f} (ec,max = {ecmax:.6f})\n"
        s += f"Concrete: {self.conc}\n"
        Fcw, Mcw = self.Cw(xu, ecmax)
        Fcf, Mcf = self.Cf(xu)
        Fcw /= 1e3
        Fcf /= 1e3
        Mcw /= 1e6
        Mcf /= 1e6
        Fc = Fcw + Fcf
        Mc = Mcw + Mcf
        s += f"{' ':>8}{'dc':>6}{'xc':>6}{'Bars':>12}{'Area':>10}{'Stress':>8}{'x NA':>10}{'Strain':>12}"
        s += f"{'fs':>10}{'fc':>10}{'Force':>10}{'Moment':>10}\n"
        s += f"{'Concrete':>8}{' ':>38}{'C':>4}{xu:10.2f}{ecmax:12.4e}{' ':>10}"
        s += f"{self.conc.fd:10.2f}{Fc:10.2f}{Mc:10.2f}\n"
        Ft = 0.0
        Mt = 0.0
        for L in d:
            s += f"{'Rebar':>8}{L['dc']:6}{L['xc']:6}{L['bars']:>12}{L['area']:10.2f}{L['type']:>8}"
            s += f"{abs(float(L['x'])):10.2f}{L['es']:12.4e}{L['fs']:10.2f}"
            if L["type"] == "C":
                s += f"{L['fc']:10.2f}"
                Fc += float(L["F"]) / 1e3
                Mc += float(L["M"]) / 1e6
            else:
                s += f"{' ':>10}"
                Ft += float(L["F"]) / 1e3
                Mt += float(L["M"]) / 1e6
            F = float(L["F"]) / 1e3
            M = float(L["M"]) / 1e6
            s += f"{F:10.2f}{M:10.2f}\n"
        s += f"{' ':>92}{'-'*10}{'-'*10}\n"
        s += f"{abs(Fc - Ft):102.2f}{(Mc + Mt):10.2f}\n"
        s += f"SHEAR\n{self.shear_steel}\n"
        s += f"CAPACITY\n{'Mu = ':>5}{self.Mu(xu, ecmax)/1e6:.2f} kNm\n"
        vuc, vus = self.Vu(xu)
        vu = vuc + sum(vus)
        s += f"{'Vu = ':>5}{vu/1e3:.2f} kN\n"
        return s
