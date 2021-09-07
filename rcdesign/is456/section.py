"""Class to represent reinforced concrete cross sections"""


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
    def __init__(self, b: float, D: float, conc: Concrete,
                 t_steel: RebarGroup, c_steel: RebarGroup,
                 shear_steel: ShearReinforcement, clear_cover: float):
        super().__init__(DesignForceType.BEAM, clear_cover)
        self.b = b
        self.D = D
        self.conc = conc
        self.t_steel = t_steel
        self.c_steel = c_steel
        self.shear_steel = shear_steel

    def xumax(self, d: float = 1):
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
        return xu, Mu

    def pt(self):
        d = self.eff_d()
        ast = self.t_steel.area
        return ast / (self.b * d) * 100

    def tauc(self):
        return self.conc.tauc(self.pt())

    def __repr__(self):  # pragma: no cover
        s = f"Size: {self.b} x {self.D}\nTension Steel: {self.t_steel}\n"
        s += f"Compression Steel: {self.c_steel}"
        return s

    def report(self, xu: float, ecu: float):  # pragma: no cover
        from rich import box
        from rich.console import Console
        from rich.table import Table

        console = Console()
        console.print(f"[bold blue]Rectangular Beam Section[/bold blue] {self.b} x {self.D}  (xu = {xu:.2f})")
        print(f"Concrete: {self.conc.fck}, Tension Steel: {self.t_steel.rebar.fy}", end = "")
        if self.c_steel:
            print(f", Compression Steel: {self.c_steel.rebar.fy}")
        else:
            print()
        print("Units: Distance in mm, Area in mm^2, Force in kN, Moment about NA in kNm")
        console.print("Flexure Capacity", style="bold blue")
        C = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        Mc = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.b
        c_table = Table(show_header=True, header_style="magenta", title_justify="left",
            box=box.SQUARE, title_style="bold red", title="Concrete in Compression")
        c_table.add_column("C (kN)", width=8, justify="right")
        c_table.add_column("M (kNm)", width=8, justify="right")
        c_table.add_row(f"{C/1e3:8.2f}", f"{Mc/1e6:8.2f}")
        console.print(c_table)
        c1_table = Table(show_header=True, header_style="magenta", title_justify="left",
             title_style="bold red", box=box.SQUARE, title="Compression Reinforcement")
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
            for layer in self.c_steel.layers:
                x = xu - layer.dc
                esc = ecu / xu * x
                fsc = self.c_steel.rebar.fs(esc)
                fcc = self.conc.fc(x / xu, self.conc.fd)
                Fsc = layer.area * (fsc - fcc)
                C += Fsc
                Msc = Fsc * x
                Mc += Msc
                c1_table.add_row(
                    f"{layer.dc:4.0f}", f"{layer.bar_list()}", f"{layer.area:8.2f}", f"{x:8.2f}", f"{esc:12.4e}",
                    f"{fsc:8.2f}", f"{fcc:8.2f}", f"{Fsc/1e3:8.2f}", f"{Msc/1e6:8.2f}"
                )
            c1_table.add_row(" ", " ", f"{self.c_steel.area:8.2f}", " ", " ", "Mc", f"{C/1e3:8.2f}", f"{Mc/1e6:8.2f}")
        else:
            c1_table.add_row("-", "-", "-", "-", "-", "-", "-", "-")
        console.print(c1_table)
        T = 0
        Mt = 0
        table = Table(show_header=True, header_style="magenta", title_justify="left",
            box=box.SQUARE, title_style="bold red", title="Tension Reinforcement")
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
                f"{layer.dc:4.0f}", f"{layer.bar_list()}", f"{layer.area:8.2f}", f"{x:8.2f}", f"{est:12.4e}",
                f"{fst:8.2f}", f"{' ':8}", f"{Fst/1e3:8.2f}", f"{Mst/1e6:8.2f}")
        table.add_row(" ", " ", f"{self.t_steel.area:8.2f}", " ", " ", "Total T", f"{T/1e3:8.2f}", f"{Mt/1e6:8.2f}")
        M = Mc + Mt
        table.add_row(" ", " ", " ", " ", " ", "C-T, Mu",
            f"[bold magenta]{(C - T)/1e3:8.4f}[/bold magenta]",
            f"[bold magenta]{M/1e6:8.2f}[/bold magenta]")
        console.print(table)
        console.print("Shear Capacity", style="bold blue")
        Vu = self.Vu()
        console.print(f"{self.shear_steel.__repr__()}, Vu (kN) = {Vu/1e3:.2f}")

    # def design(self, Mu: float, Vu: float = 0, Tu: float = 0):
    #     d = self.D - self.clear_cover - 25.0
    #     mulim = self.mulim(d) * self.conc.fck * self.b * d**2
    #     if abs(Mu) > mulim:
    #         print(f'Doubly reinforced section (Mu,lim = {mulim / 1e6}')
    #     else:
    #         print(f'Singly reinforced section (Mu,lim = {mulim / 1e6})')

    def eff_d(self):
        return self.D - self.t_steel._dc()

    def Vu(self, nlegs: int = 0, bar_dia: int = 0, sv: float = 0):
        if nlegs > 0:
            self.shear_steel.nlegs = nlegs
        if bar_dia > 0:
            self.shear_steel.bar_dia = bar_dia
        if sv > 0:
            self.shear_steel.sv = sv
        pt = self.t_steel.area * 100 / (self.b * self.eff_d())
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * self.eff_d()
        Vus = self.shear_steel.rebar.fd * self.shear_steel.Asv * self.eff_d() / self.shear_steel._sv
        return Vuc + Vus

    def sv(self, Vu: float, nlegs: int, bar_dia: int, mof: float = 25):
        self.shear_steel.nlegs = nlegs
        self.shear_steel.bar_dia = bar_dia

        pt = self.t_steel.area * 100 / (self.b * self.eff_d())
        tauc = self.conc.tauc(pt)
        Vuc = tauc * self.b * self.eff_d()

        Vus = Vu - Vuc
        self._sv = self.shear_steel.rebar.fd * self.shear_steel._Asv * self.eff_d() / Vus
        self._sv = floor(self._sv, mof)
        return self._sv


"""Class to repersent flanged section"""


@dataclass
class FlangedBeamSection(RectBeamSection):
    def __init__(self, bw: float, D: float, bf: float, Df: float,
                 conc: Concrete, t_steel: RebarGroup, c_steel: RebarGroup,
                 shear_steel: Rebar, clear_cover: float):
        super().__init__(bw, D, conc, t_steel, c_steel, shear_steel, clear_cover)
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

    def C(self, xu: float, ecu: float):
        # Compression force and moment due to concrete of web
        C1 = self.conc.area(0, 1, self.conc.fd) * xu * self.bw
        M1 = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.bw
        # Compression force and moment due to compression reinforcement bars
        if self.c_steel:
            C2, M2 = self.c_steel.force_compression(xu, self.conc, ecu)
        else:
            C2 = 0.0
            M2 = 0.0
        # Compression force and moment due to concrete of flange
        df = xu if xu <= self.Df else self.Df
        x1 = xu - df
        C3 = self.conc.area(x1/xu, 1, self.conc.fd) * xu * (self.bf - self.bw)
        M3 = self.conc.moment(x1/xu, 1, self.conc.fd) * xu**2 * (self.bf - self.bw)
        # print('---', C2, C1, C3)
        # print('---', M2, M1, M3)
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
        s = f'Flanged Beam Section {self.bw}x{self.D} {self.bf}x{self.Df}\n'
        s += self.conc.__repr__() + '\n'
        s += f"{self.c_steel.layers[0]}\n"
        return s

    def C_T(self, x: float, ecu: float):
        C, _ = self.C(x, ecu)
        T, _ = self.T(x, ecu)
        return C - T

    def xu(self, ecu: float):
        x1, x2 = rootsearch(self.C_T, self.t_steel.layers[0].dc, self.D, 10, ecu)
        x = brentq(self.C_T, x1, x2, args=(ecu,))
        return x

    def analyse(self, ecu: float):
        xu = self.xu(ecu)
        Mu = self.Mu(self.eff_d(), xu, ecu)
        return xu, Mu

    def report(self, xu: float, ecu: float):  # pragma: no cover
        from rich.console import Console

        console = Console()
        console.print(f"Flanged Beam Section {self.b} x {self.D}, bf = {self.bf}, Df = {self.Df}, (xu = {xu:.2f})", style="bold blue")
        print("Units: Distance in mm, Area in mm^2, Force in kN, Moment in kNm")
        console.print("Flexure Capacity", style="bold blue")
        Cw = self.conc.area(0, 1, self.conc.fd) * xu * self.b
        Mw = self.conc.moment(0, 1, self.conc.fd) * xu**2 * self.b

        print(f"{' ':54}{'C (kN)':>8} {'M (kNm)':>8}")
        print(f"{'Concrete in Compression':54}{Cw/1e3:8.2f} {Mw/1e6:8.2f}")
        console.print("Compression Reinforcement", style="bold red", end="")
        if self.c_steel:
            print()
            print(f"{'dc':>4} {'Area':>8} {'x':>8} {'Strain':>12} {'f_sc':>8} {'f_cc':>8} {'C':>8} {'M':>8}")
            for layer in self.c_steel.layers:
                x = xu - layer.dc
                esc = ecu / xu * x
                fsc = self.c_steel.rebar.fs(esc)
                fcc = self.conc.fc(x / xu, self.conc.fd)
                Fsc = layer.area * (fsc - fcc)
                Cw += Fsc
                Msc = Fsc * x
                Mw += Msc
                print(f"{layer.dc:4.0f} {layer.area:8.2f} {x:8.2f} {esc:12.4e} {fsc:8.2f} {fcc:8.2f} {Fsc/1e3:8.2f} {Msc/1e6:8.2f}")
        else:
            print(f"{'-':>37} {'-':>8}")
        print('-'*71)
        print(f"{' '*54}{Cw/1e3:8.2f} {Mw/1e6:8.2f}")
        console.print("Tension Reinforcement", style="bold red")
        T = 0
        Mt = 0
        print(f"{'dc':>4} {'Area':>8} {'x':>8} {'Strain':>12} {'f_st':>8} {' ':8} {'T (kN)':>8} {'M (kNm)':>8}")
        for layer in self.t_steel.layers:
            x = self.D - xu - layer.dc
            est = ecu / xu * x
            fst = self.t_steel.rebar.fs(est)
            Fst = layer.area * fst
            T += Fst
            Mst = Fst * x
            Mt += Mst
            print(f"{layer.dc:4.0f} {layer.area:8.2f} {x:8.2f} {est:12.4e} {fst:8.2f} {' ':8} {Fst/1e3:8.2f} {Mst/1e6:8.2f}")
        print(f"{' '*54}{T/1e3:8.2f} {Mt/1e6:8.2f}")
        M = Mw + Mt
        print('-'*71)
        print(f"{' '*54}{(Cw - T)/1e3:8.4f} {M/1e6:8.2f}")
        console.print("Shear Capacity", style="bold blue")
        print(self.shear_steel.__repr__())
        Vu = self.Vu()
        print(f'Ultimate shear capacity (kN): {Vu/1e3:.2f}')
