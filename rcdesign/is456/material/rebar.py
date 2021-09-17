"""Classes to represent reinforcement bars, layers of reinforcement bars
and groups of reinforcement layers"""

import numpy as np
from math import pi, sin, isclose
from typing import Tuple, List, Union
from dataclasses import dataclass
from abc import ABC, abstractmethod

from .concrete import Concrete


# Rebar class


@dataclass
class Rebar(ABC):  # pragma: no cover
    label: str
    fy: float
    gamma_m = 1.15
    density = 78.5
    Es = 2e5

    @property
    def fd(self):
        return self.fy / self.gamma_m

    def es_min(self):
        return self.fd / self.Es + 0.002

    @abstractmethod
    def fs(self, es):
        pass


"""Mild steel reinforcement bars as defined in IS456:2000 with a
well defined yield point"""


class RebarMS(Rebar):
    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)

    def __repr__(self):  # pragma: no cover
        return f"{self.label:>6}: Type={'MS':4} fy={self.fy} fd={self.fd:.2f}"

    def _fs(self, es: float) -> float:
        _es = abs(es)
        _esy = self.fd / self.Es

        if _es < _esy:
            return es * self.Es
        else:
            return self.fd

    def fs(self, es: float) -> float:
        if isinstance(es, np.ndarray):
            return np.array([self._fs(x) for x in es])
        else:
            return self._fs(es)


"""High yield strength deformed bars as defined in IS456:2000 with piece-wise
linear stress-strain relation between 0.8 to 1.0 times design strength"""


class RebarHYSD(Rebar):
    inel = np.array(
        [
            [0.8, 0.85, 0.9, 0.95, 0.975, 1.0],
            [0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002],
        ]
    ).T

    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)
        self.es = RebarHYSD.inel.copy()
        self.es[:, 0] = self.es[:, 0] * self.fy / self.gamma_m
        self.es[:, 1] = self.es[:, 0] / self.Es + self.es[:, 1]

    def __repr__(self) -> str:  # pragma: no cover
        return f"{self.label:>6}: Type={'HYSD'} fy={self.fy} fd={self.fd:.2f}"

    def _fs(self, es: float) -> float:
        _es = abs(es)
        i = 0
        fd1 = self.es[i, 0]
        es1 = self.es[i, 1]
        if _es <= es1:
            return es * self.Es
        else:
            for i in range(1, 6):
                fd2 = self.es[i, 0]
                es2 = self.es[i, 1]
                if _es <= es2:
                    break
                else:
                    fd1, es1 = fd2, es2
            if _es < es2:
                fs = fd1 + (fd2 - fd1) / (es2 - es1) * (_es - es1)
            else:
                fs = fd2
            return np.sign(es) * fs

    def fs(self, es: float) -> Union[float, np.ndarray]:
        if isinstance(es, np.ndarray):
            return np.array([self._fs(x) for x in es])
        else:
            return self._fs(es)


"""Layer of reinforcement bars"""


@dataclass
class RebarLayer:
    dia: List[int]  # List of bar diameters, left to right, all of same type
    _dc: float  # Distance of centre of layer from edge of section
    _xc: float = 0.0  # Distance from compression edge
    stress_type: str = ""  # Type of stress, C (compression) or T (tension)

    def max_dia(self) -> int:
        return max(self.dia)

    @property
    def area(self) -> float:
        return sum([d ** 2 for d in self.dia]) * pi / 4

    @property
    def dc(self) -> float:
        return self._dc

    @dc.setter
    def dc(self, _dc) -> None:
        self._dc = _dc

    @property
    def xc(self) -> float:
        return self._xc

    def calc_xc(self, D: float) -> float:
        if self.dc > 0:
            self._xc = self.dc
        else:
            self._xc = D + self.dc

    def calc_stress_type(self, xu: float) -> str:
        if isclose(self._xc, xu):
            self.stress_type = "neutral"
        elif self._xc < xu:
            self.stress_type = "compression"
        elif self._xc > 0:
            self.stress_type = "tension"
        return self.stress_type

    def x(self, xu: float) -> float:
        return xu - self._xc

    def __repr__(self) -> str:  # pragma: no cover
        s = "Dia: "
        b = ""
        for bardia in self.dia:
            b += f"{bardia}, "
        b = "[" + b[:-2] + "]"
        s += f"{b} at {self.dc}. Area: {self.area:.2f} (xc = {self._xc:.2f})"
        return s

    def fs(self, xu: float, rebar: Rebar, ecu: float) -> float:
        es = ecu / xu * self.x(xu)
        return rebar._fs(es)

    def force_tension(
        self, xu: float, rebar: Rebar, ecu: float
    ) -> Tuple[float, float, str]:
        x = self.x(xu)
        es = ecu / xu * x
        fs = rebar.fs(es)

        _f = self.area * fs
        _m = _f * x
        result = {"x": x, "es": es, "f_st": fs, "T": _f, "M": _m}
        return _f, _m, result

    def force_compression(
        self, xu: float, conc: Concrete, rebar: Rebar, ecu: float
    ) -> Tuple[float, float, str]:
        x = xu - self._xc
        esc = ecu / xu * x
        fsc = rebar._fs(esc)  # Stress in compression steel
        fcc = conc.fc(x / xu, conc.fd)  # Stress in concrete
        _f = self.area * (fsc - fcc)
        _m = _f * x
        result = {"x": x, "esc": esc, "f_sc": fsc, "f_cc": fcc, "C": _f, "M": _m}
        return _f, _m, result

    def bar_list(self, sep=";") -> str:
        d = dict()
        for bar_dia in self.dia:
            if bar_dia in d.keys():
                d[bar_dia] += 1
            else:
                d[bar_dia] = 1
        s = ""
        for bar_dia in sorted(d.keys()):
            s += f"{d[bar_dia]}-{bar_dia} "
        s = s.rstrip().replace(" ", sep)
        return s

    def __lt__(self, b) -> bool:
        return self._xc < b._xc

    def __le__(self, b) -> bool:
        return self._xc <= b._xc

    def __eq__(self, b) -> bool:
        return self._xc == b._xc

    def __ne__(self, b) -> bool:
        return self._xc != b._xc

    def __gt__(self, b) -> bool:
        return self._xc > b._xc

    def __ge__(self, b) -> bool:
        return self._xc >= b._xc


"""Group of reinforcement bars"""


@dataclass
class RebarGroup:
    rebar: Rebar  # Rebar object
    layers: List[RebarLayer]  # List of layers of bars, in any order from edge

    @property
    def area(self) -> float:
        return sum([layer.area for layer in self.layers])

    def calc_xc(self, D: float) -> float:
        for L in self.layers:
            L.calc_xc(D)

    @property
    def centroid(self) -> float:
        a = 0.0
        m = 0.0
        for L in self.layers:
            _a = L.area
            a += _a
            m += _a * L._xc
        return m / a

    @property
    def dc(self) -> float:
        a = 0.0
        m = 0.0
        for L in self.layers:
            _a = L.area
            a += _a
            m += _a * L.dc
        return m / a

    def has_comp_steel(self, xu: float) -> bool:
        for L in self.layers:
            if L._xc < xu:
                return True
        return False

    def area_comp(self, xu: float) -> float:
        a = 0.0
        for L in self.layers:
            if L._xc < xu:
                a += L.area
        return a

    def area_tension(self, xu: float) -> float:
        a = 0.0
        for L in self.layers:
            if L._xc > xu:
                a += L.area
        return a

    def calc_stress_type(self, xu: float) -> None:
        for L in self.layers:
            L.calc_stress_type(xu)

    def force_moment(
        self, xu: float, conc: Concrete, ecu: float
    ) -> Tuple[float, float, float, float]:
        fc = ft = mc = mt = 0.0
        for L in self.layers:
            if L._xc < xu:  # in compression
                _fc, _mc, _ = L.force_compression(xu, conc, self.rebar, ecu)
                fc += _fc
                mc += _mc
            else:
                x = L._xc - xu
                _ft, _mt, _ = L.force_tension(xu, self.rebar, ecu)
                _ft = abs(_ft)
                ft += _ft
                mt += _mt
        return fc, mc, ft, mt

    def force_tension(self, xu: float, ecu: float) -> Tuple[float, float]:
        f = m = 0.0
        for L in self.layers:
            if L._xc > xu:
                D_xu = L._xc - xu
                _f, _m, _ = L.force_tension(xu, self.rebar, ecu)
                f += _f
                m += _m
        return f, m

    def force_compression(
        self, xu: float, conc: Concrete, ecu: float
    ) -> Tuple[float, float]:
        _f = _m = 0.0
        for L in self.layers:
            if L._xc < xu:
                __f, __m, _ = L.force_compression(xu, conc, self.rebar, ecu)
                _f += __f
                _m += __m
        return _f, _m

    def dc_max(self, D: float) -> Tuple[float, float]:
        x1 = 0
        dx_max = 0
        for L in sorted(self.layers):
            d = L.max_dia()
            x2 = L._xc - d / 2
            dx = x2 - x1
            if dx > dx_max:
                dx_max = dx
                xmin = x1
                xmax = x2
            x1 = x2 + d
        dx = D - x1
        if dx > dx_max:
            dx_max = dx
            xmin = x1
            xmax = D
        return (xmin, xmax)

    def __repr__(self) -> str:  # pragma: no cover
        sl = "layers" if len(self.layers) > 1 else "layer"
        s = f"Rebar Group {self.rebar.label} in {len(self.layers)} {sl}\n"
        s += f"{'dc':>10}{'xc':>10}{'Bars':>12}{'Area':>10}\n"
        for L in self.layers:
            s += f"{L.dc:10.2f}{L._xc:10.2f}{L.bar_list():>12}{L.area:10.2f}\n"
        s += f"{' ':20}{'-'*22}\n{' ':20}{'Total':>12}{self.area:10.2f}"
        return s


"""Shear reinforcement"""


class ShearReinforcement(ABC):  # pragma: no cover
    def __init__(self, rebar: Rebar, _Asv: float = 0.0, _sv: float = 0.0):
        self.rebar = rebar
        self._Asv = _Asv
        self._sv = _sv

    @abstractmethod
    def Asv(self):
        pass


"""Vertical or inclined stirrups as shear reinforcement"""


class Stirrups(ShearReinforcement):
    def __init__(
        self,
        rebar: Rebar,
        _nlegs: int,
        _bar_dia: int,
        _sv: float = 0.0,
        _alpha_deg: float = 90,
    ):
        self.rebar = rebar
        self._nlegs = _nlegs
        self._bar_dia = _bar_dia
        self._alpha_deg = _alpha_deg
        self._Asv = self.Asv
        self._sv = _sv

    @property
    def Asv(self) -> float:
        self._Asv = self.nlegs * pi * self.bar_dia ** 2 / 4
        return self._Asv

    @property
    def nlegs(self) -> int:
        return self._nlegs

    @nlegs.setter
    def nlegs(self, n) -> None:
        self._nlegs = n
        self._Asv = self.nlegs * pi * self.bar_dia ** 2 / 4

    @property
    def bar_dia(self) -> int:
        return self._bar_dia

    @bar_dia.setter
    def bar_dia(self, dia) -> None:
        self._bar_dia = dia
        self._Asv = self.nlegs * pi * self.bar_dia ** 2 / 4

    @property
    def sv(self) -> float:
        return self._sv

    @sv.setter
    def sv(self, _sv: float) -> float:
        self._sv = _sv
        self._Asv = self.nlegs * pi * self.bar_dia ** 2 / 4
        return self._Asv

    def calc_sv(self, Vus: float, d: float) -> float:
        if (self._alpha_deg < 45) or (self._alpha_deg > 90):
            return
        alpha_rad = self._alpha_deg * pi / 180
        self._sv = self.rebar.fd * self.Asv * d * sin(alpha_rad) / Vus
        return self._sv

    def __repr__(self) -> str:  # pragma: no cover
        sh_rein = "Vertical" if self._alpha_deg == 90 else "Inclined"
        s = f"Shear reinforcement: {sh_rein} Stirrups "
        s += f"{self._nlegs}-{self._bar_dia} @ {self._sv} c/c"
        if self._alpha_deg != 90:
            s += " inclined at {self._alpha_deg} degrees"
        return s


"""Bent up bars as shear reinforcement"""


class BentupBars(Stirrups):
    def __init__(
        self, rebar: Rebar, bars: List[int], _sv: float = 0.0, _alpha_deg: float = 45
    ):
        self.rebar = rebar
        self.bars = bars
        self._alpha_deg = _alpha_deg
        self._Asv = self.Asv
        self._sv = _sv

    @property
    def Asv(self) -> float:
        area = 0.0
        for bar_dia in self.bars:
            area += bar_dia ** 2
        return pi * area / 4
