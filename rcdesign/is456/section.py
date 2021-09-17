"""Class to represent reinforced concrete cross sections"""

from math import isclose
from enum import Enum

from typing import Tuple, List, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod
from os import sep
from scipy.optimize import brentq


from .material.concrete import Concrete
from .material.rebar import Rebar, RebarGroup, ShearReinforcement
from rcdesign.utils import floor

from ..utils import rootsearch


# DesignForce class


class DesignForceType(Enum):
    BEAM = 1
    COLUMN = 2
    SLAB = 3
    SHEARWALL = 4


class Section(ABC):  # pragma: no cover
    def __init__(self, design_force_type, clear_cover):
        self.design_force_type = design_force_type
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
        # t_steel: RebarGroup,
        # c_steel: RebarGroup,
        long_steel: RebarGroup,
        shear_steel: ShearReinforcement,
        clear_cover: float,
        stress_type: str = "Unknown",
    ):
        super().__init__(DesignForceType.BEAM, clear_cover)
        self.b = b
        self.D = D
        self.conc = conc
        self.shear_steel = shear_steel
        self.long_steel = long_steel
        self.calc_xc()

    def calc_xc(self) -> float:
        self.long_steel.calc_xc(self.D)

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

    def C(self, xu: float, ecu: float) -> float:
        C, _, M, _ = self.force_moment(xu, ecu)
        return C, M

    def force_moment(self, xu: float, ecu: float) -> Tuple[float, float, float, float]:
        self.adjust_x(xu)
        Fc = Mc = Ft = Mt = 0.0
        Fcc = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        Mcc = self.conc.moment(0, 1, self.conc.fd) * xu ** 2 * self.b
        Fc += Fcc
        Mc += Mcc
        Fsc = Msc = Fst = Mst = 0.0
        Fsc, Msc, Fst, Mst = self.long_steel.force_moment(xu, self.conc, ecu)
        Fc += Fsc
        Mc += Msc
        Ft += Fst
        Mt += Mst
        return Fc, Ft, Mc, Mt

    def T(self, xu: float, ecu: float) -> Tuple[float, float]:
        _, _T, _, _M = self.force_moment(xu, ecu)
        return _T, _M

    def C_T(self, x: float, ecu: float) -> float:
        # C, _ = self.C(x, ecu)
        # T, _ = self.T(x, ecu)
        self.adjust_x(x)
        C, T, _, _ = self.force_moment(x, ecu)
        return C - T

    def xu(self, ecu: float) -> float:
        dc_max = 10

        x1, x2 = rootsearch(self.C_T, dc_max, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def Mu(self, xu: float, ecu: float) -> float:
        # Assuming tension steel to produce an equal tension force as C
        C, M = self.C(xu, ecu)
        return M + C * (self.eff_d(xu) - xu)

    def analyse(self, ecu: float) -> Tuple[float, float]:
        xu = self.xu(ecu)
        Mu = self.Mu(xu, ecu)
        return xu, Mu

    def tauc(self, xu: float) -> float:
        return self.conc.tauc(self.pt(xu))

    def __repr__(self) -> str:  # pragma: no cover
        s = f"Size: {self.b} x {self.D}\nTension Steel: {self.long_steel}\n"
        # s += f"Compression Steel: {self.c_steel}"
        return s

    def has_compr_steel(self, xu: float) -> bool:
        for L in self.long_steel.layers:
            if L._xc < xu:
                return True
        return False

    def report(self, xu: float, ecu: float) -> str:  # pragma: no cover
        self.adjust_x(xu)
        s = f"Rectangular Beam Section {self.b} x {self.D}  (xu = {xu:.2f})\n"
        s += f"Concrete: {self.conc.fck}, Tension Steel: {self.long_steel.rebar.fy:.2f}"
        if self.has_compr_steel(xu):
            s += f", Compression Steel: {self.long_steel.rebar.fy:.2f}\n"
        else:
            s += "\n"
        s += (
            "Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm\n"
        )
        s += "Flexure Capacity\n"
        Fcc = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        Mcc = self.conc.moment(0, 1, self.conc.fd) * xu ** 2 * self.b
        s += "Concrete in Compression\n"
        s += f"{' ':60}{'C (kN)':>8}{'M (kNm)':>8}\n{' ':60}{Fcc/1e3:8.2f}{Mcc/1e6:8.2f}\n"

        # Compression steel
        if self.has_compr_steel(xu):
            sc = "Compression Steel\n"
            sc += f"{'dc':>8}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_sc':>8}"
            sc += f"{'f_cc':>8}{'C (kN)':>8}{'M (kNm)':>8}\n"
        else:
            sc = ""
        st = "Tension Steel\n"
        st += f"{'dc':>8}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_st':>8}{' ':8}"
        st += f"{'T (kN)':>8}{'M (kNm)':>8}\n"
        Fsc = Msc = 0.0
        Fst = Mst = 0.0
        for L in self.long_steel.layers:
            if L._xc < xu:  # Layer of compression steel
                x = xu - L._xc
                esc = ecu / xu * x
                fsc = self.long_steel.rebar.fs(esc)
                fcc = self.conc.fc(x / xu, self.conc.fd)
                _Fsc = L.area * (fsc - fcc)
                _Msc = _Fsc * x
                Fsc += _Fsc
                Msc += _Msc
                sc += f"{L.dc:8.1f}{L.bar_list():>8}{L.area:8.2f}{x:8.2f}{esc:12.4e}"
                sc += f"{fsc:8.2f}{fcc:8.2f}{_Fsc/1e3:8.2f}{_Msc/1e6:8.2f}\n"
            else:
                x = L._xc - xu
                est = ecu / xu * x
                fst = self.long_steel.rebar.fs(est)
                _Fst = L.area * fst
                _Mst = _Fst * x
                Fst += _Fst
                Mst += _Mst
                st += f"{L.dc:8.1f}{L.bar_list():>8}{L.area:8.2f}{x:8.2f}{est:12.4e}"
                st += f"{fst:8.2f}{' ':8}{_Fst/1e3:8.2f}{_Mst/1e6:8.2f}\n"
        Fc = Fcc + Fsc
        Ft = Fst
        Mc = Mcc + Msc
        Mt = Mst
        sc += f"{' ':16}{'-'*8}{' ':36}{'-'*16}\n"
        sc += f"{' ':16}{self.long_steel.area_comp(xu):8.2f}{' ':36}{Fc/1e3:8.2f}{Mc/1e6:8.2f}\n"
        st += f"{' ':16}{'-'*8}{' ':36}{'-'*16}\n"
        st += f"{' ':16}{self.long_steel.area_tension(xu):8.2f}{' ':36}{Ft/1e3:8.2f}{Mt/1e6:8.2f}\n"
        s += sc
        s += st
        s += f"{' ':60}{'='*16}\n"
        F = Fc - Ft
        M = Mc + Mt
        if isclose(F, 0.0, abs_tol=1e-4):
            s += f"{' ':60}{0.00:>8}"
        else:
            s += f"{' ':60}{(Fc - Ft)/1e3:8.2}"
        s += f"{M/1e6:8.2f}\n"
        # Shear reinforcement
        s += f"Shear Capacity\n"
        s += f"{self.shear_steel.__repr__()}\n"
        tauc, Vus, Vuc = self.Vu(xu, separate_output=True)
        s += f"pst = {self.pt(xu):.2f}%, d = {self.eff_d(xu):.2f}, "
        s += f"tau_c (N/mm^2) = {tauc:.2f}\n"
        Vu = Vuc + Vus
        s += f"Vuc (kN) = {Vuc/1e3:.2f}, Vus = {Vus/1e3:.2f}, Vu (kN) = {Vu/1e3:.2f}"
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
        return pt

    def Vu(
        self,
        xu: float,
        nlegs: int = 0,
        bar_dia: int = 0,
        sv: float = 0,
        separate_output=False,
    ) -> Union[Tuple[float, float], Tuple[float, float, float]]:
        if nlegs > 0:
            self.shear_steel.nlegs = nlegs
        if bar_dia > 0:
            self.shear_steel.bar_dia = bar_dia
        if sv > 0:
            self.shear_steel.sv = sv
        # pt = self.long_steel.area * 100 / (self.b * self.eff_d())
        pt = self.pt(xu)
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * self.eff_d(xu)
        Vus = (
            self.shear_steel.rebar.fd
            * self.shear_steel.Asv
            * self.eff_d(xu)
            / self.shear_steel._sv
        )
        if separate_output:
            return tauc, Vuc, Vus
        else:
            return Vuc + Vus

    def sv(
        self, xu: float, Vu: float, nlegs: int, bar_dia: int, mof: float = 25
    ) -> float:
        self.shear_steel.nlegs = nlegs
        self.shear_steel.bar_dia = bar_dia

        pt = self.pt(xu)
        d = self.eff_d(xu)
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * d

        Vus = Vu - Vuc
        self._sv = self.shear_steel.rebar.fd * self.shear_steel._Asv * d / Vus
        self._sv = floor(self._sv, mof)
        return self._sv


"""Class to repersent flanged section"""


@dataclass
class FlangedBeamSection(RectBeamSection):
    def __init__(
        self,
        bw: float,
        D: float,
        bf: float,
        Df: float,
        conc: Concrete,
        long_steel: RebarGroup,
        # t_steel: RebarGroup,
        # c_steel: RebarGroup,
        shear_steel: Rebar,
        clear_cover: float,
    ):
        super().__init__(bw, D, conc, long_steel, shear_steel, clear_cover)
        bw: float
        # D: float
        self.bf = bf
        self.Df = Df

    @property
    def bw(self) -> float:
        return self.b

    @bw.setter
    def bw(self, _bw) -> None:
        self.b = _bw

    def Cw(self, xu: float, ecu: float) -> Tuple[float, float]:
        C = self.conc.area(0, 1, self.conc.fd) * xu * self.bw
        M = self.conc.moment(0, 1, self.conc.fd) * xu ** 2 * self.bw
        return C, M

    def Cf(self, xu: float) -> Tuple[float, float]:
        df = xu if xu <= self.Df else self.Df
        x1 = xu - df
        C = self.conc.area(x1 / xu, 1, self.conc.fd) * xu * (self.bf - self.bw)
        M = self.conc.moment(x1 / xu, 1, self.conc.fd) * xu ** 2 * (self.bf - self.bw)
        return C, M

    def C(self, xu: float, ecu: float) -> Tuple[float, float]:
        # Compression force and moment due to concrete of web
        C1, M1 = self.Cw(xu, ecu)
        # Compression force and moment due to compression reinforcement bars
        if self.has_compr_steel(xu):
            C2, M2 = self.long_steel.force_compression(xu, self.conc, ecu)
        else:
            C2 = M2 = 0.0

        # Compression force and moment due to concrete of flange
        C3, M3 = self.Cf(xu)

        # Sum it all up
        C = C1 + C2 + C3
        M = M1 + M2 + M3
        return C, M

    def Mu(self, d: float, xu: float, ecu: float) -> float:
        # Based on compression force C, assuming the right amount of tension steel
        C, M = self.C(xu, ecu)
        Mu = M + C * (d - xu)
        return Mu

    def __repr__(self) -> str:  # pragma: no cover
        s = f"Flanged Beam Section {self.bw}x{self.D} {self.bf}x{self.Df}\n"
        s += self.conc.__repr__() + "\n"
        s += f"{self.c_steel.layers[0]}\n"
        return s

    def C_T(self, x: float, ecu: float) -> float:
        C, _ = self.C(x, ecu)
        T, _ = self.T(x, ecu)
        return C - T

    def xu(self, ecu: float) -> float:
        # x1, x2 = rootsearch(self.C_T, self.t_steel.layers[0].dc, self.D, 10, ecu)
        x1, x2 = rootsearch(self.C_T, 10, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def analyse(self, ecu: float) -> Tuple[float, float]:
        xu = self.xu(ecu)
        Mu = self.Mu(self.eff_d(xu), xu, ecu)
        return xu, Mu

    def report(self, xu: float, ecu: float) -> str:  # pragma: no cover
        s = f"Flanged Beam Section {self.b} x {self.D}, bf = {self.bf}, Df = {self.Df}, (xu = {xu:.2f})\n"
        s += f"Concrete: {self.conc.fck}, Tension Steel: {self.long_steel.rebar.fy}"
        s += f", Compression Steel: {self.long_steel.rebar.fy}"
        s += "\nUnits: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm\n"
        s += "Flexure Capacity\n"
        # Web of beam
        Cw, Mw = self.Cw(xu, ecu)
        # Flange of beam
        Cf, Mf = self.Cf(xu)
        Fcc = Cw + Cf
        Mcc = Mw + Mf
        Fc = Fcc
        Mc = Mcc
        cw = f"{' ':24}{'Cw (kN)':>8}{'Mw (kN)':>8}{'Cf (kN)':>8}{'Mf (kN)':>8}{'C (kN)':>8}{'M (kNm)':>8}\n"
        cw += "-" * 72 + "\n"
        cw += f"{' ':24}{Cw/1e3:8.2f}{Mw/1e6:8.2f}{Cf/1e3:8.2f}{Mf/1e6:8.2f}{Fcc/1e3:8.2f}{Mcc/1e6:8.2f}\n"
        s += cw
        # Compression steel
        Fsc = Msc = 0.0
        Ft = Mt = 0.0
        if self.has_compr_steel(xu):
            sc = "Compression Reinforcement\n"
            sc = f"{'dc':>4}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_sc':>8}{'f_cc':>8}{'C (kN)':>8}{'M (kNm)':>8}\n"
            sc += "-" * 72 + "\n"
        else:
            sc = ""
        st = f"{'dc':>4}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_st':>8}{' ':>8}{'C (kN)':>8}{'M (kNm)':>8}\n"
        st += "-" * 72 + "\n"
        for L in self.long_steel.layers:
            if L._xc < xu:
                # Compression steel
                x = xu - L._xc
                esc = ecu / xu * x
                fsc = L.rebar.fs(esc)
                fcc = self.conc.fc(x / xu, self.conc.fd)
                _Fsc = L.area * (fsc - fcc)
                _Msc = Fsc * x
                Fsc += _Fsc
                Msc = _Msc
                sc += f"{L.dc:4.0f} {L.area:8.2f} {x:8.2f} {esc:12.4e} {fsc:8.2f} {fcc:8.2f} {_Fsc/1e3:8.2f} {_Msc/1e6:8.2f}\n"
            else:
                # Tension steel
                x = L._xc - xu
                est = ecu / xu * x
                fst = self.long_steel.rebar.fs(est)
                _Fst = L.area * fst
                _Mst = _Fst * x
                Ft += _Fst
                Mt += _Mst
                st += f"{L.dc:4.0f}{L.bar_list():>8}{L.area:8.2f}{x:8.2f}{est:12.4e}{fst:8.2f}{' ':8}{_Fst/1e3:8.2f}{_Mst/1e6:8.2f}\n"
        sc += f"{' ':56}{'-'*16}\n{' ':56}{Fc/1e3:8.2f}{Mc/1e6:8.2f}\n"
        st += f"{' ':56}{'-'*16}\n{' ':56}{Ft/1e3:8.2f}{Mt/1e6:8.2f}\n"
        Fc += Fsc
        Mc += Msc
        s += sc
        s += "Tension Reinforcement\n"
        s += st
        if isclose(Fc, Ft):
            C_T = "0.00"
        else:
            C_T = f"{(Fc - Ft)/1e6:8.2f}"
        s += f"{' ':56}{'='*16}\n{' ':56}{C_T:>8}{(Mc+Mt)/1e6:8.2f}"
        return s
