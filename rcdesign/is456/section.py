"""Class to represent reinforced concrete cross sections"""

from math import isclose
from enum import Enum

# from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod
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
        # self.t_steel = t_steel
        # self.c_steel = c_steel
        self.shear_steel = shear_steel
        self.long_steel = long_steel
        self.calc_xc()

    def calc_xc(self):
        self.long_steel.calc_xc(self.D)

    def adjust_x(self, xu: float):
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

    def xumax(self, d: float = 1):
        es_min = self.long_steel.rebar.es_min()
        return 0.0035 / (es_min + 0.0035) * d

    def mulim(self, d: float):
        xumax = self.xumax() * d
        return (17 / 21) * self.conc.fd * self.b * xumax * (d - (99 / 238) * xumax)

    def C(self, xu: float, ecu: float):
        C, _, M, _ = self.force_moment(xu, ecu)
        return C, M

    def force_moment(self, xu: float, ecu: float):
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

    def T(self, xu: float, ecu: float):
        # _T, _M = self.t_steel.force_tension(xu, self.D - xu, ecu)
        _, _T, _, _M = self.force_moment(xu, ecu)
        return _T, _M

    def C_T(self, x: float, ecu: float):
        # C, _ = self.C(x, ecu)
        # T, _ = self.T(x, ecu)
        self.adjust_x(x)
        C, T, _, _ = self.force_moment(x, ecu)
        return C - T

    def xu(self, ecu: float):
        dc_max = 10
        # if self.c_steel:
        #     dc_max += self.c_steel.dc_max()

        x1, x2 = rootsearch(self.C_T, dc_max, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def Mu(self, xu: float, ecu: float):
        # Assuming tension steel to produce an equal tension force as C
        C, M = self.C(xu, ecu)
        return M + C * (self.eff_d(xu) - xu)

    def analyse(self, ecu: float):
        xu = self.xu(ecu)
        Mu = self.Mu(xu, ecu)
        return xu, Mu

    def tauc(self, xu: float):
        return self.conc.tauc(self.pt(xu))

    def __repr__(self):  # pragma: no cover
        s = f"Size: {self.b} x {self.D}\nTension Steel: {self.long_steel}\n"
        # s += f"Compression Steel: {self.c_steel}"
        return s

    def has_compr_steel(self, xu: float):
        for L in self.long_steel.layers:
            if L._xc < xu:
                return True
        return False

    def report(self, xu: float, ecu: float):  # pragma: no cover
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
        s += f"{' ':56}{'C (kN)':>8}{'M (kNm)':>8}\n{' ':56}{Fcc/1e3:8.2f}{Mcc/1e6:8.2f}\n"

        # Compression steel
        sc = "Compression Steel\n"
        sc += f"{'dc':>4}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_sc':>8}"
        sc += f"{'f_cc':>8}{'C (kN)':>8}{'M (kNm)':>8}\n"
        st = "Tension Steel\n"
        st += f"{'dc':>4}{'Bars':>8}{'Area':>8}{'x':>8}{'Strain':>12}{'f_st':>8}{' ':8}"
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
                sc += (
                    f"{abs(L.dc):4.0f}{L.bar_list():>8}{L.area:8.2f}{x:8.2f}{esc:12.4e}"
                )
                sc += f"{fsc:8.2f}{fcc:8.2f}{_Fsc/1e3:8.2f}{_Msc/1e6:8.2f}\n"
            else:
                # D_xu = self.D - xu
                x = L._xc - xu
                est = ecu / xu * x
                fst = self.long_steel.rebar.fs(est)
                _Fst = L.area * fst
                _Mst = _Fst * x
                Fst += _Fst
                Mst += _Mst
                st += (
                    f"{abs(L.dc):4.0f}{L.bar_list():>8}{L.area:8.2f}{x:8.2f}{est:12.4e}"
                )
                st += f"{fst:8.2f}{' ':8}{_Fst/1e3:8.2f}{_Mst/1e6:8.2f}\n"
        Fc = Fcc + Fsc
        Ft = Fst
        Mc = Mcc + Msc
        Mt = Mst
        sc += f"{' ':56}{'-'*16}\n"
        sc += f"{' ':56}{Fc/1e3:8.2f}{Mc/1e6:8.2f}\n"
        st += f"{' ':56}{'-'*16}\n"
        st += f"{' ':56}{Ft/1e3:8.2f}{Mt/1e6:8.2f}\n"
        s += sc
        s += st
        s += f"{' ':56}{'='*16}\n"
        F = Fc - Ft
        M = Mc + Mt
        if isclose(F, 0.0, abs_tol=1e-4):
            s += f"{' ':56}{0.00:>8}"
        else:
            s += f"{' ':56}{(Fc - Ft)/1e3:8.2}"
        s += f"{M/1e6:8.2f}\n"
        # Shear reinforcement
        s += f"Shear Capacity\n"
        s += f"{self.pt(xu):.2f} d = {self.eff_d(xu):.2f}\n"
        Vu = self.Vu(xu)
        s += f"{self.shear_steel.__repr__()}, Vu (kN) = {Vu/1e3:.2f}"
        return s

    # def design(self, Mu: float, Vu: float = 0, Tu: float = 0):
    #     d = self.D - self.clear_cover - 25.0
    #     mulim = self.mulim(d) * self.conc.fck * self.b * d**2
    #     if abs(Mu) > mulim:
    #         print(f'Doubly reinforced section (Mu,lim = {mulim / 1e6}')
    #     else:
    #         print(f'Singly reinforced section (Mu,lim = {mulim / 1e6})')

    def eff_d(self, xu: float):
        a = 0.0
        m = 0.0
        for L in sorted(self.long_steel.layers):
            if L._xc >= xu:
                _a = L.area
                _m = _a * L._xc
                a += _a
                m += _m
        return m / a

    def pt(self, xu: float):
        d = self.eff_d(xu)
        ast = 0.0
        for L in sorted(self.long_steel.layers):
            if L._xc > xu:
                ast += L.area
        pt = ast / (self.b * d) * 100
        return pt

    def Vu(self, xu: float, nlegs: int = 0, bar_dia: int = 0, sv: float = 0):
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
        return Vuc + Vus

    def sv(self, xu: float, Vu: float, nlegs: int, bar_dia: int, mof: float = 25):
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
    def bw(self):
        return self.b

    @bw.setter
    def bw(self, _bw):
        self.b = _bw

    def Cw(self, xu: float, ecu: float):
        C = self.conc.area(0, 1, self.conc.fd) * xu * self.bw
        M = self.conc.moment(0, 1, self.conc.fd) * xu ** 2 * self.bw
        return C, M

    def Cf(self, xu: float):
        df = xu if xu <= self.Df else self.Df
        x1 = xu - df
        C = self.conc.area(x1 / xu, 1, self.conc.fd) * xu * (self.bf - self.bw)
        M = self.conc.moment(x1 / xu, 1, self.conc.fd) * xu ** 2 * (self.bf - self.bw)
        return C, M

    def C(self, xu: float, ecu: float):
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

    def Mu(self, d: float, xu: float, ecu: float):
        # Based on compression force C, assuming the right amount of tension steel
        C, M = self.C(xu, ecu)
        Mu = M + C * (d - xu)
        return Mu

    def __repr__(self):  # pragma: no cover
        s = f"Flanged Beam Section {self.bw}x{self.D} {self.bf}x{self.Df}\n"
        s += self.conc.__repr__() + "\n"
        s += f"{self.c_steel.layers[0]}\n"
        return s

    def C_T(self, x: float, ecu: float):
        C, _ = self.C(x, ecu)
        T, _ = self.T(x, ecu)
        return C - T

    def xu(self, ecu: float):
        # x1, x2 = rootsearch(self.C_T, self.t_steel.layers[0].dc, self.D, 10, ecu)
        x1, x2 = rootsearch(self.C_T, 10, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def analyse(self, ecu: float):
        xu = self.xu(ecu)
        Mu = self.Mu(self.eff_d(xu), xu, ecu)
        return xu, Mu

    def report(self, xu: float, ecu: float):  # pragma: no cover
        from rich import box
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print(
            f"Flanged Beam Section {self.b} x {self.D}, bf = {self.bf}, Df = {self.Df}, (xu = {xu:.2f})",
            style="bold blue",
        )
        print(
            f"Concrete: {self.conc.fck}, Tension Steel: {self.t_steel.rebar.fy}", end=""
        )
        if self.c_steel:
            print(f", Compression Steel: {self.c_steel.rebar.fy}")
        else:
            print()
        print(
            "Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm"
        )
        console.print("Flexure Capacity", style="bold blue")
        # Web of beam
        Cw, Mw = self.Cw(xu, ecu)
        # Flange of beam
        Cf, Mf = self.Cf(xu)
        C = Cw + Cf
        Mc = Mw + Mf
        c_table = Table(
            show_header=True,
            header_style="magenta",
            title_justify="left",
            box=box.SQUARE,
            title_style="bold red",
            title="Concrete in Compression",
        )
        c_table.add_column("Cw (kN)", width=8, justify="right")
        c_table.add_column("Cf (kN)", width=8, justify="right")
        c_table.add_column("C (kN)", width=8, justify="right")
        c_table.add_column("Mw (kN)", width=8, justify="right")
        c_table.add_column("Mf (kN)", width=8, justify="right")
        c_table.add_column("M (kNm)", width=8, justify="right")
        c_table.add_row(
            f"{Cw/1e3:8.2f}",
            f"{Cf/1e3:8.2f}",
            f"{C/1e3:8.2f}",
            f"{Mw/1e6:8.2f}",
            f"{Mf/1e6:8.2f}",
            f"{Mc/1e6:8.2f}",
        )
        console.print(c_table)
        # Compression steel
        c1_table = Table(
            show_header=True,
            header_style="magenta",
            title_justify="left",
            title_style="bold red",
            box=box.SQUARE,
            title="Compression Reinforcement",
        )
        c1_table.add_column("dc", width=4, justify="right")
        c1_table.add_column("Bars", width=8, justify="right")
        c1_table.add_column("Area", width=8, justify="right")
        c1_table.add_column("x", width=8, justify="right")
        c1_table.add_column("Strain", width=12, justify="right")
        c1_table.add_column("f_sc", width=8, justify="right")
        c1_table.add_column("f_cc", width=8, justify="right")
        c1_table.add_column("C (kN)", width=8, justify="right")
        c1_table.add_column("M (kNm)", width=8, justify="right")
        if self.c_steel:
            print()
            print(
                f"{'dc':>4} {'Area':>8} {'x':>8} {'Strain':>12} {'f_sc':>8} {'f_cc':>8} {'C':>8} {'M':>8}"
            )
            for layer in self.c_steel.layers:
                x = xu - layer.dc
                esc = ecu / xu * x
                fsc = self.c_steel.rebar.fs(esc)
                fcc = self.conc.fc(x / xu, self.conc.fd)
                Fsc = layer.area * (fsc - fcc)
                C += Fsc
                Mc += Fsc * x
                print(
                    f"{layer.dc:4.0f} {layer.area:8.2f} {x:8.2f} {esc:12.4e} {fsc:8.2f} {fcc:8.2f} {Fsc/1e3:8.2f} {Mc/1e6:8.2f}"
                )
        else:
            c1_table.add_row("-", "-", "-", "-", "-", "-", "-", "-", "-")
        c1_table.add_row(
            " ", " ", " ", " ", " ", " ", "Total", f"{C/1e3:8.2f}", f"{Mc/1e6:8.2f}"
        )
        console.print(c1_table)
        T = 0
        Mt = 0
        table = Table(
            show_header=True,
            header_style="magenta",
            title_justify="left",
            box=box.SQUARE,
            title_style="bold red",
            title="Tension Reinforcement",
        )
        table.add_column("dc", width=4, justify="right")
        table.add_column("Bars", width=8, justify="right")
        table.add_column("Area", width=8, justify="right")
        table.add_column("x", width=8, justify="right")
        table.add_column("Strain", width=12, justify="right")
        table.add_column("f_st", width=8, justify="right")
        table.add_column(" ", width=8, justify="right")
        table.add_column("T (kN)", width=8, justify="right")
        table.add_column("M (kNm)", width=8, justify="right")
        for layer in self.t_steel.layers:
            x = self.D - xu - layer.dc
            est = ecu / xu * x
            fst = self.t_steel.rebar.fs(est)
            Fst = layer.area * fst
            T += Fst
            Mst = Fst * x
            Mt += Mst
            table.add_row(
                f"{layer.dc:4.0f}",
                f"{layer.bar_list()}",
                f"{layer.area:8.2f}",
                f"{x:8.2f}",
                f"{est:12.4e}",
                f"{fst:8.2f}",
                f"{' ':8}",
                f"{Fst/1e3:8.2f}",
                f"{Mst/1e6:8.2f}",
            )
        table.add_row(
            " ",
            " ",
            f"{self.t_steel.area:8.2f}",
            " ",
            " ",
            " ",
            "Total",
            f"{T/1e3:8.2f}",
            f"{Mt/1e6:8.2f}",
        )
        M = Mc + Mt
        if isclose(C - T, 0.0, abs_tol=1e-4):
            c_t = f"{0.00:>8}"
        else:
            c_t = f"{(C - T)/1e3:8.2}"
        table.add_row(
            " ",
            " ",
            " ",
            " ",
            " ",
            " ",
            "C-T, Mu",
            f"[bold magenta]{c_t}[/bold magenta]",
            f"[bold magenta]{M/1e6:8.2f}[/bold magenta]",
        )
        console.print(table)
        # Shear reinforcement
        console.print("Shear Capacity", style="bold blue")
        Vu = self.Vu()
        console.print(f"{self.shear_steel.__repr__()}, Vu (kN) = {Vu/1e3:.2f}")
