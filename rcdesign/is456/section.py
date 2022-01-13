"""Class to represent reinforced concrete cross sections"""

from math import isclose
from enum import Enum
from typing import Tuple, List

# from dataclasses import dataclass
# from abc import ABC, abstractmethod
from scipy.optimize import brentq

from rcdesign.is456 import ecy, ecu
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarGroup,
    ShearRebarGroup,
    LateralTie,
    ShearRebarType,
    StressType,
    StressLabel,
)
from rcdesign.utils import rootsearch, underline, header


# DesignForce class


class DesignForceType(Enum):
    BEAM = 1
    COLUMN = 2
    SLAB = 3
    SHEARWALL = 4


"""Class to repersent a rectangular beam section"""


class RectBeamSection:
    def __init__(
        self,
        b: float,
        D: float,
        csb: LSMStressBlock,
        conc: Concrete,
        long_steel: RebarGroup,
        shear_steel: ShearRebarGroup,
        clear_cover: float,
    ):
        self.design_force_type = DesignForceType.BEAM
        self.csb = csb
        self.conc = conc
        self.long_steel = long_steel
        self.clear_cover = clear_cover
        self.b = b
        self.D = D

        self.shear_steel = shear_steel
        self.calc_xc()

    def calc_xc(self) -> None:
        self.long_steel.calc_xc(self.D)
        return None

    def calc_stress_type(self, xu: float) -> None:
        self.calc_xc()
        self.long_steel.calc_stress_type(xu)

    def C(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        Fc, Mc, _, _ = self.F_M(xu, ecmax)
        return Fc, Mc

    def T(self, xu: float, ecmax: float) -> Tuple[float, float]:
        _, _, Ft, Mt = self.F_M(xu, ecmax)
        return Ft, Mt

    def C_T(self, xu: float, ecmax: float = ecu) -> float:
        self.calc_stress_type(xu)
        C, _, T, _ = self.F_M(xu, ecmax)
        return C - T

    def F_M(self, xu: float, ecmax: float = ecu) -> Tuple[float, float, float, float]:
        # sb = LSMStressBlock("LSM Flexure")
        self.calc_stress_type(xu)
        Fc = Mc = Ft = Mt = 0.0
        # Compression force - concrete
        k = xu / self.D
        Fcc = self.csb.C(0, k, k, ecmax) * self.conc.fd * self.b * self.D
        Mcc = self.csb.M(0, k, k, ecmax) * self.conc.fd * self.b * self.D ** 2
        # Compression force - compression steel
        Fsc, Msc, Fst, Mst = self.long_steel.force_moment(
            xu, self.csb, self.conc, ecmax
        )
        # Tension force in tension steel
        Ft, Mt = self.long_steel.force_tension(xu, ecmax)
        Fc = Fcc + Fsc
        Mc = Mcc + Msc
        return Fc, Mc, Ft, Mt

    def xu(self, ecmax: float = ecu) -> float:
        dc_max = 10

        x1, x2 = rootsearch(self.C_T, dc_max, self.D, 10, ecmax)
        x = brentq(self.C_T, x1, x2, args=(ecmax,))
        return x

    def Mu(self, xu: float, ecmax: float = ecu) -> float:
        # Assuming area of tension steel to be such as to produce a tension force equal to C
        _, Mc = self.C(xu, ecmax)
        _, Mt = self.T(xu, ecmax)
        M = Mc + Mt
        return M

    def tauc(self, xu: float) -> float:
        return self.conc.tauc(self.pt(xu))

    def __repr__(self) -> str:
        ecmax = self.csb.ecu
        xu = self.xu(ecmax)
        return self.report(xu, ecmax)

    def has_compr_steel(self, xu: float) -> bool:
        for L in self.long_steel.layers:
            if L._xc < xu:
                return True
        return False

    def report(self, xu: float, ecmax: float = ecu) -> str:  # pragma: no cover
        self.calc_xc()
        self.calc_stress_type(xu)
        k = xu / self.D
        ecy = self.csb.ecy
        hdr0 = f"RECTANGULAR BEAM SECTION: {self.b} x {self.D}"
        s = f"{header(hdr0, '~')}\n"
        s += f"{header('FLEXURE', '=')}\nEquilibrium NA = {xu:.2f} (k = {k:.2f}) (ec_max = {ecmax:.6f})\n\n"
        fcc = self.csb._fc_(ecmax) * self.conc.fd
        Fc = self.b * self.csb.C(0, k, k, ecmax) * self.conc.fd * self.D
        Mc = self.csb.M(0, k, k) * self.conc.fd * self.b * self.D ** 2
        hdr1 = f"{'fck':>6} {' ':>8} {' ':>12} {'ec_max':>12} {'Type':>4} "
        hdr1 += f"{' ':>8} {'f_cc':>6} {'C (kN)':>8} {'M (kNm)':>8}"
        s += hdr1 + "\n" + underline(hdr1) + "\n"
        s += f"{self.conc.fck:6.2f} {' ':>8} {' ':>12} {ecmax:12.8f} {'C':>4} {' ':>8} {fcc:6.2f} "
        s += f"{Fc / 1e3:8.2f} {Mc/ 1e6:8.2f}\n{underline(hdr1)}\n\n"
        Ft = 0.0
        Mt = 0.0
        hdr2 = f"{'fy':>6} {'Bars':>12} {'xc':>8} {'Strain':>12} {'Type':>4} {'f_sc':>8} {'f_cc':>6}"
        hdr2 += f" {'C (kN)':>8} {'M (kNm)':>8}"
        s += f"{hdr2}\n{underline(hdr2)}\n"
        for L in sorted(self.long_steel.layers):
            z = k - (L._xc / self.D)
            esc = self.csb.ec(z, k) * ecy
            stress_type = L.stress_type(xu)
            fsc = L.rebar.fs(esc)
            s += f"{L.rebar.fy:6.0f} {L.bar_list():>12} {L._xc:8.2f} {esc:12.8f} "
            s += f"{StressLabel[stress_type][0]:>4} {fsc:8.2f} "
            if stress_type == StressType.STRESS_COMPRESSION:
                fcc = self.csb.fc(z, k, ecmax) * self.conc.fd
                c = L.area * (fsc - fcc)
                s += f"{fcc:6.2f} "
            elif L._stress_type == StressType.STRESS_TENSION:
                c = L.area * fsc
                s += f"{' ':>6} "

            m = c * (k * self.D - L._xc)
            s += f"{c/1e3:8.2f} {m/1e6:8.2f}\n"
            Ft += c
            Mt += m
        s += f"{underline(hdr2)}\n"
        if len(self.long_steel.layers) > 1:
            C_M = f"{Ft/1e3:8.2f} {Mt/1e6:8.2f}"
            s += f"{' '*62} {C_M}\n{' '*62} {underline(C_M, '=')}\n"
        F = 0.0 if isclose(Fc + Ft, 0, abs_tol=1e-10) else Fc + Ft
        C_M = f"{F/1e3:8.2f} {(Mc + Mt)/1e6:8.2f}"
        s += f"{' ':>62} {C_M}\n"
        s += f"{header('SHEAR', '=')}\n"
        tauc = self.conc.tauc(self.pt(xu))
        area = self.b * self.eff_d(xu)
        vuc = area * tauc
        hdr3 = f"{'Type':>14} {' ':>14} {'tau_c':>6} {'Area (mm^2)':>16} {' ':>8} {' ':>8} {'V_uc (kN)':>8}"
        s += f"{header(hdr3)}\n"
        s += f"{'Concrete':>14} {' ':>14} {tauc:6.2f} {area:16.2f} {' ':>8} {' ':>8} {vuc/1e3:8.2f}\n"
        s += f"{underline(hdr3)}\n"
        hdr4 = f"{'Type':>14} {'Variant':>14} {'f_y':>6} {'Bars':>16} {'s_v':>8} {'A_sv':>8} {'V_us (kN)':>8}"
        s += f"{header(hdr4)}\n"
        vus = 0.0
        for sh_rein in self.shear_steel.shear_reinforcement:
            data = sh_rein.report(self.eff_d(xu))
            s += f"{data['label']:>14} {data['type']:>14} {data['fy']:6} "
            if data["sh_type"] in [
                ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP,
                ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP,
            ]:
                bar_info = f"{data['legs']}-{data['bar_dia']}#"
            else:
                bar_info = f"{data['bars']}"
            s += f"{bar_info:>16} {data['sv']:8.1f} {data['Asv']:8.2f} {data['Vus']/1e3:8.2f}\n"
            vus += data["Vus"]
        vu = f"{(vuc + vus)/1e3:8.2f}"
        s += f"{' ':>71} {underline(vu, '=')}\n{' ':>71} {vu}\n"
        s += (
            f"{header('CAPACITY', '=')}\n{'Mu = ':>5}{self.Mu(xu, ecmax)/1e6:.2f} kNm\n"
        )
        Vuc, Vus = self.Vu(xu)
        Vu = Vuc + sum(Vus)
        s += f"{'Vu = ':>5}{Vu/1e3:.2f} kN\n"
        return s

    def eff_d(self, xu: float) -> float:
        _, ct = self.long_steel.centroid(xu)
        return ct

    def pt(self, xu: float) -> float:
        ast = 0.0
        for L in sorted(self.long_steel.layers):
            if L._xc > xu:
                ast += L.area
        d = self.eff_d(xu)
        pt = ast / (self.b * d) * 100
        return pt

    def Vu(self, xu: float) -> Tuple[float, List[float]]:
        # print("\nstart::RectBeamSection.Vu(xu)", xu)
        pt = self.pt(xu)
        # print("stop::RectBeamSection.Vu(xu)\n")
        tauc = self.conc.tauc(pt)
        d = self.eff_d(xu)
        vuc = tauc * self.b * d
        vus = self.shear_steel.Vus(d)
        return vuc, vus

    def analyse(self, ecmax: float = ecu) -> Tuple[float, float]:
        xu = self.xu(ecmax)
        Mu = self.Mu(xu, ecmax)
        return xu, Mu


"""Class to repersent flanged section"""


class FlangedBeamSection(RectBeamSection):
    def __init__(
        self,
        bw: float,
        D: float,
        bf: float,
        Df: float,
        csb: LSMStressBlock,
        conc: Concrete,
        long_steel: RebarGroup,
        shear_steel: ShearRebarGroup,
        clear_cover: float,
    ):
        super().__init__(bw, D, csb, conc, long_steel, shear_steel, clear_cover)
        self.bf = bf
        self.Df = Df

    @property
    def bw(self) -> float:
        return self.b

    @bw.setter
    def bw(self, _bw) -> None:
        self.b = _bw

    def Cw(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        k = xu / self.D
        area = self.csb.C(0, k, k, ecmax) * self.conc.fd
        moment = self.csb.M(0, k, k, ecmax) * self.conc.fd

        C = area * self.bw * self.D
        M = moment * self.bw * self.D ** 2
        return C, M

    def Cf(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        df = xu if xu <= self.Df else self.Df
        k = xu / self.D
        z1 = (xu - df) / self.D
        z2 = k
        area = self.csb.C(z1, z2, k, ecmax) * self.conc.fd
        moment = self.csb.M(z1, z2, k, ecmax) * self.conc.fd
        C = area * self.D * (self.bf - self.bw)
        M = moment * self.D ** 2 * (self.bf - self.bw)
        return C, M

    def C_M(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        # Compression force and moment due to concrete of web
        C1, M1 = self.Cw(xu, ecmax)
        C2, M2 = self.Cf(xu, ecmax)
        # Compression force and moment due to compression reinforcement bars
        if self.has_compr_steel(xu):
            C3, M3 = self.long_steel.force_compression(xu, self.csb, self.conc, ecmax)
        else:
            C3 = M3 = 0.0

        # Sum it all up
        C = C1 + C2 + C3
        M = M1 + M2 + M3
        return C, M

    def Mu(self, xu: float, ecmax: float = ecu) -> float:
        # Cc and Ct must be equal for beams, if not, NA chosen does not conform to equilibrium
        Cc, Mc = self.C_M(xu, ecmax)
        Ct, Mt = self.T(xu, ecmax)
        Mu = Mc + Mt
        return Mu

    def __repr__(self) -> str:
        ecmax = self.csb.ecu
        xu = self.xu(ecmax)
        return self.report(xu, ecmax)

    def C_T(self, xu: float, ecmax: float = ecu) -> float:
        C, _ = self.C_M(xu, ecmax)
        T, _ = self.T(xu, ecmax)
        return C - T

    def xu(self, ecmax: float = ecu) -> float:
        x1, x2 = rootsearch(self.C_T, 10, self.D, 10, ecmax)
        x = brentq(self.C_T, x1, x2, args=(ecmax,))
        return x

    def report(self, xu: float, ecmax: float = ecu) -> str:  # pragma: no cover
        self.calc_xc()
        self.calc_stress_type(xu)
        k = xu / self.D
        ecy = self.csb.ecy
        hdr0 = f"FLANGED BEAM SECTION - Web: {self.b} x {self.D}, Flange: {self.bf} x {self.Df}"
        s = f"{header(hdr0, '~')}\n"
        s += f"{header('FLEXURE', '=')}\nEquilibrium NA = {xu:.2f} (ec_max = {ecmax:.6f})\n\n"
        Fcw, Mcw = self.Cw(xu, ecmax)
        Fcf, Mcf = self.Cf(xu)
        Fc = Fcw + Fcf
        Mc = Mcw + Mcf
        hdr1 = f"{'fck':>6} {'Breadth':>10} {'Depth':>10} {'ec_min':>12}  {'ec_max':>12} {'Type':>6} "
        hdr1 += f"{'C (kN)':>8} {'M (kNm)':>8}"
        # Web
        s += hdr1 + "\n" + underline(hdr1) + "\n"
        s += f"{self.conc.fck:6.0f} {self.bw:10.2f} {self.D:10.2f} {0:12.8f}  {ecmax:12.8f} {'C':>6} "
        s += f"{Fcw/1e3:8.2f} {Mcw/1e6:8.2f}\n"
        # Flange
        s += f"{self.conc.fck:6.0f} {self.bf:10.2f} {self.Df:10.2f} {' ':>12}  {ecmax:12.8f} {'C':>6} "
        s += f"{Fcf/1e3:8.2f} {Mcf/1e6:8.2f}\n"
        s += f"{underline(hdr1)}\n"
        s += f"{' ':>62} {(Fcw+Fcf)/1e3:8.2f} {(Mcw+Mcf)/1e6:8.2f}\n"
        hdr2 = f"{'fy':>6} {'Bars':>12} {'xc':>8} {'Strain':>12} {'Type':>4} {'f_sc':>8} {'f_cc':>6}"
        hdr2 += f" {'C (kN)':>8} {'M (kNm)':>8}"
        s += f"\n{hdr2}\n{underline(hdr2)}\n"
        Ft = 0.0
        Mt = 0.0
        for L in sorted(self.long_steel.layers):
            z = k - (L._xc / self.D)
            esc = self.csb.ec(z, k) * ecy
            stress_type = L.stress_type(xu)
            fsc = L.rebar.fs(esc)
            s += f"{L.rebar.fy:6.0f} {L.bar_list():>12} {L._xc:8.2f} {esc:12.8f} "
            s += f"{StressLabel[stress_type][0]:>4} {fsc:8.2f} "
            if stress_type == StressType.STRESS_COMPRESSION:
                fcc = self.csb.fc(z, k, ecmax) * self.conc.fd
                c = L.area * (fsc - fcc)
                s += f"{fcc:6.2f} "
            else:
                c = L.area * fsc
                s += f"{' ':>6} "
            m = c * (k * self.D - L._xc)
            s += f"{c/1e3:8.2f} {m/1e6:8.2f}\n"
            Ft += c
            Mt += m
        s += f"{underline(hdr2)}\n"
        if len(self.long_steel.layers) > 1:
            C_M = f"{Ft/1e3:8.2f} {Mt/1e6:8.2f}"
            s += f"{' ':>62} {C_M}\n{' ':>62} {underline(C_M, '=')}\n"
        F = 0.0 if isclose(Fcw + Fcf + Ft, 0, abs_tol=1e-10) else Fcw + Fcf + Ft
        s += f"{' ':>62} {F/1e3:8.2f} {(Mc + Mt)/1e6:8.2f}\n"

        s += f"{header('SHEAR', '=')}\n"
        tauc = self.conc.tauc(self.pt(xu))
        area = self.b * self.eff_d(xu)
        vuc = area * tauc
        hdr3 = f"{'Type':>14} {' ':>14} {'tau_c':>6} {'Area (mm^2)':>16} {' ':>8} {' ':>8} {'V_uc (kN)':>8}"
        s += f"{header(hdr3)}\n"
        s += f"{'Concrete':>14} {' ':>14} {tauc:6.2f} {area:16.2f} {' ':>8} {' ':>8} {vuc/1e3:8.2f}\n"
        s += f"{underline(hdr3)}\n"
        hdr4 = f"{'Type':>14} {'Variant':>14} {'f_y':>6} {'Bars':>16} {'s_v':>8} {'A_sv':>8} {'V_us (kN)':>8}"
        s += f"{header(hdr4)}\n"
        vus = 0.0
        for sh_rein in self.shear_steel.shear_reinforcement:
            data = sh_rein.report(self.eff_d(xu))
            s += f"{data['label']:>14} {data['type']:>14} {data['fy']:6} "
            if data["sh_type"] in [
                ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP,
                ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP,
            ]:
                bar_info = f"{data['legs']}-{data['bar_dia']}#"
            else:
                bar_info = f"{data['bars']}"
            s += f"{bar_info:>16} {data['sv']:8.1f} {data['Asv']:8.2f} {data['Vus']/1e3:8.2f}\n"
            vus += data["Vus"]
        vu = f"{(vuc + vus)/1e3:8.2f}"
        s += f"{' ':>71} {underline(vu, '=')}\n{' ':>71} {vu}\n"
        s += (
            f"{header('CAPACITY', '=')}\n{'Mu = ':>5}{self.Mu(xu, ecmax)/1e6:.2f} kNm\n"
        )
        Vuc, Vus = self.Vu(xu)
        Vu = Vuc + sum(Vus)
        s += f"{'Vu = ':>5}{Vu/1e3:.2f} kN\n"
        return s


class RectColumnSection:
    def __init__(
        self,
        b: float,
        D: float,
        csb: LSMStressBlock,
        conc: Concrete,
        long_steel: RebarGroup,
        lat_ties: LateralTie,
        clear_cover: float,
    ):
        self.design_force_type = DesignForceType.COLUMN
        self.csb = csb
        self.conc = conc
        self.long_steel = long_steel
        self.clear_cover = clear_cover
        self.b = b
        self.D = D
        self.long_steel = long_steel
        self.lat_ties = lat_ties

    @property
    def Asc(self) -> float:
        return self.long_steel.area

    def k(self, xu: float) -> float:
        return xu / self.D

    def C_M(self, xu: float) -> Tuple[float, float]:
        self.long_steel.calc_xc(self.D)
        k = self.k(xu)
        if xu <= self.D:
            z1 = 0.0
            z2 = k
        else:
            z1 = k - 1
            z2 = k
        a = self.csb.C(z1, z2, k)
        Cc = a * self.conc.fd * self.b * self.D
        m = self.csb.M(z1, z2, k)
        Mc = m * self.conc.fd * self.b * self.D ** 2
        Cs = 0.0
        Ms = 0.0
        for L in self.long_steel.layers:
            asc = L.area
            x = xu - L.xc
            z = x / self.D
            esc = self.csb.ec(z, k) * self.csb.ecy
            fsc = L.rebar.fs(esc)
            fcc = self.csb.fc(z, k) * self.conc.fd
            if fsc >= 0:
                _Cs = asc * (fsc - fcc)
            else:
                _Cs = asc * fsc
            Cs += _Cs
            Ms += _Cs * abs(x)
        return Cc + Cs, Mc + Ms

    def __repr__(self) -> str:
        s = f"RECTANGULAR COLUMN {self.b} x {self.D}\n"
        s += f"Concrete: {self.conc} Clear Cover: {self.clear_cover}\n"
        self.long_steel.calc_xc(self.D)
        s += f"{'fy':>6} {'Bars':>8} {'xc':>8}\n"
        for L in self.long_steel.layers:
            s += f"{L.rebar.fy:6.0f} {L.bar_list():>8} {L._xc:8.2f}\n"
        return s

    def report(self, xu: float) -> str:
        k = xu / self.D
        ecy = self.csb.ecy
        s = f"RECTANGULAR COLUMN {self.b} x {self.D} xu = {xu:.2f} (k = {k:.2f})\n"
        s += f"Concrete: {self.conc} Clear Cover: {self.clear_cover}\n"
        # Concrete
        fd = self.conc.fd
        if k <= 1:
            z1 = 0.0
        else:
            z1 = k - 1
        z2 = k
        ecmin = self.csb.ec(z1, k) * ecy
        ecmax = self.csb.ec(z2, k) * ecy
        fsc1 = self.csb.fc(z1, k) * fd
        fsc2 = self.csb.fc(z2, k) * fd
        Cc = self.csb.C(z1, z2, k) * fd * self.b * self.D
        Mc = self.csb.M(z1, z2, k) * fd * self.b * self.D ** 2
        hdr1 = f"{'fck':>6} {' ':>8} {'ecmin':>12} {'ecmax':>12} {'Type':>4} {'fsc1':>8} {'fsc2':>6} "
        hdr1 += f"{'Cc':>8} {'Mc':>8}"
        s += f"\n{header(hdr1)}\n"
        # s += header(hdr1) + "\n"
        s += f"{self.conc.fck:6.2f} {' ':>8} {ecmin:12.8f} {ecmax:12.8f} {'C':>4} {fsc1:8.2f} {fsc2:6.2f} "
        s += f"{Cc/1e3:8.2f} {Mc/1e6:8.2f}\n{'-'*len(hdr1)}\n"
        # Longitudinal steel
        self.long_steel.calc_xc(self.D)
        self.long_steel.calc_stress_type(xu)
        hdr2 = f"{'fy':>6} {'Bars':>12} {'xc':>8} {'Strain':>12} {'Type':>4} {'fsc':>8} {'fcc':>6} "
        hdr2 += f"{'C (kN)':>8} {'M (kNm)':>8}"
        s += f"\n{header(hdr2)}\n"
        ecy = self.csb.ecy
        cc = 0.0
        mm = 0.0
        for L in sorted(self.long_steel.layers):
            z = k - (L._xc / self.D)
            esc = self.csb.ec(z, k) * ecy
            str_type = L.stress_type(xu)
            fsc = L.rebar.fs(esc)
            if str_type == 1:
                fcc = self.csb.fc(z, k) * self.conc.fd
                c = L.area * (fsc - fcc)
            else:
                c = L.area * fsc
                fcc = 0.0
            m = c * (k * self.D - L._xc)
            s += f"{L.rebar.fy:6.0f} {L.bar_list():>12} {L._xc:8.2f} {esc:12.8f} {StressLabel[str_type][0]:>4} "
            if str_type == 1:
                s += f"{fsc:8.2f} {fcc:6.2f}"
            else:
                s += f"{fsc:8.2f} {'--':>6}"
            s += f" {c/1e3:8.2f} {m/1e6:8.2f}\n"
            cc += c
            mm += m
        s += "-" * len(hdr2) + "\n"
        s += f"{' '*62} {cc/1e3:8.2f} {mm/1e6:8.2f}\n"
        C, M = self.C_M(xu)
        hdr3 = f"{C/1e3:8.2f} {M/1e6:8.2f}"
        s += f"{' ':>62} {underline(hdr3, '=')}\n{' ':>62} {hdr3}\n"
        s += f"{header('CAPACITY', '=')}\n"
        s += f"Pu = {C/1e3:10.2f} kN\nMu = {M/1e6:10.2f} kNm\n e = {M/C:10.2f} mm\n"
        return s
