"""Classes to represent reinforcement bars, layers of reinforcement bars
and groups of reinforcement layers"""

from enum import IntEnum
from math import pi, sin, cos, isclose
from typing import Tuple, List, Union, Dict, Optional
from dataclasses import dataclass
from abc import ABC, abstractmethod
import numpy as np

from .concrete import Concrete

# Rebar Enumerations


class RebarType(IntEnum):
    REBAR_MS = 1
    REBAR_HYSD = 2


RebarLabel = {RebarType.REBAR_MS: "Mild Steel", RebarType.REBAR_HYSD: "HYSD"}


class ShearRebarType(IntEnum):
    SHEAR_REBAR_VERTICAL_STIRRUP = 1
    SHEAR_REBAR_INCLINED_STIRRUP = 2
    SHEAR_REBAR_BENTUP_SINGLE = 3
    SHEAR_REBAR_BENTUP_SERIES = 4


ShearRebarLabel = {
    ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP: "Vertical stirrup",
    ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP: "Inclined stirrup",
    ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE: "Bent-up bars in single group",
    ShearRebarType.SHEAR_REBAR_BENTUP_SERIES: "Bent-up bars in series",
}

# Rebar class


class Rebar(ABC):  # pragma: no cover
    def __init__(self, label: str, fy: float, gamma_m=1.15, density=78.5, Es=2e5):
        self.label = label
        self.fy = fy
        self.gamma_m = gamma_m
        self.density = density
        self.Es = Es

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

    def __repr__(self):
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

    def __repr__(self) -> str:
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


class RebarLayer:
    def __init__(self, dia: List[int], _dc: float):
        self.dia = dia
        self._dc = _dc
        self._xc = _dc
        self.stress_type = ""

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

    def calc_xc(self, D: float) -> None:
        if self.dc > 0:
            self._xc = self.dc
        else:
            self._xc = D + self.dc
        return None

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

    def __repr__(self) -> str:
        s = "Dia: "
        b = ""
        for bardia in self.dia:
            b += f"{bardia}, "
        b = "[" + b[:-2] + "]"
        s += f"{b} at {self.dc}. Area: {self.area:.2f} (xc = {self._xc:.2f})"
        return s

    def fs(self, xu: float, rebar: Rebar, ecmax: float) -> float:
        es = ecmax / xu * self.x(xu)
        return rebar.fs(es)

    def force_tension(
        self, xu: float, rebar: Rebar, ecmax: float
    ) -> Tuple[float, float, Dict]:
        x = self.x(xu)
        es = ecmax / xu * x
        fs = rebar.fs(es)

        _f = self.area * fs
        _m = _f * x
        result = {"x": x, "es": es, "f_st": fs, "T": _f, "M": _m}
        return _f, _m, result

    def force_compression(
        self, xu: float, conc: Concrete, rebar: Rebar, ecmax: float
    ) -> Tuple[float, float, Dict]:
        x = xu - self._xc
        esc = ecmax / xu * x
        fsc = rebar.fs(esc)  # Stress in compression steel
        fcc = conc.fc(x / xu, conc.fd)  # Stress in concrete
        _f = self.area * (fsc - fcc)
        _m = _f * x
        result = {"x": x, "esc": esc, "f_sc": fsc, "f_cc": fcc, "C": _f, "M": _m}
        return _f, _m, result

    def report(
        self, xu: float, conc: Concrete, rebar: Rebar, ecmax: float
    ) -> Dict[str, Union[float, str, int]]:  # pragma: no cover
        x = self.x(xu)
        # print("***", xu, self._xc, x)

        if x >= 0:  # Compression
            esc = ecmax / xu * x
            fsc = rebar.fs(esc)
            fcc = conc.fc(x / xu, conc.fd)
            _f = self.area * (fsc - fcc)
            _m = _f * x
            d = {
                "type": "C",
                "dc": self._dc,
                "xc": self._xc,
                "bars": self.bar_list(),
                "area": self.area,
                "x": x,
                "es": esc,
                "fs": fsc,
                "fc": fcc,
                "F": _f,
                "M": _m,
            }
        else:  # Tension
            est = ecmax / xu * abs(x)
            fst = rebar.fs(est)

            _f = self.area * fst
            _m = _f * abs(x)
            d = {
                "type": "T",
                "dc": self._dc,
                "xc": self._xc,
                "bars": self.bar_list(),
                "area": self.area,
                "x": x,
                "es": est,
                "fs": fst,
                "fc": 0,
                "F": _f,
                "M": _m,
            }
        return d

    def bar_list(self, sep=";") -> str:
        d: Dict = dict()
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


class RebarGroup:
    def __init__(self, rebar: Rebar, layers: List[RebarLayer]):
        self.rebar = rebar  # Rebar object
        self.layers = layers  # List of layers of bars, in any order from edge

    @property
    def area(self) -> float:
        return sum([layer.area for layer in self.layers])

    def calc_xc(self, D: float) -> None:
        for L in self.layers:
            L.calc_xc(D)
        return None

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
        self, xu: float, conc: Concrete, ecmax: float
    ) -> Tuple[float, float, float, float]:
        fc = ft = mc = mt = 0.0
        for L in self.layers:
            if L._xc < xu:  # in compression
                _fc, _mc, _ = L.force_compression(xu, conc, self.rebar, ecmax)
                fc += _fc
                mc += _mc
            else:
                # x = L._xc - xu
                _ft, _mt, _ = L.force_tension(xu, self.rebar, ecmax)
                _ft = abs(_ft)
                ft += _ft
                mt += _mt
        return fc, mc, ft, mt

    def force_tension(self, xu: float, ecmax: float) -> Tuple[float, float]:
        f = m = 0.0
        for L in self.layers:
            if L._xc > xu:
                # D_xu = L._xc - xu
                _f, _m, _ = L.force_tension(xu, self.rebar, ecmax)
                f += _f
                m += _m
        return f, m

    def force_compression(
        self, xu: float, conc: Concrete, ecmax: float
    ) -> Tuple[float, float]:
        _f = _m = 0.0
        for L in self.layers:
            if L._xc < xu:
                __f, __m, _ = L.force_compression(xu, conc, self.rebar, ecmax)
                _f += __f
                _m += __m
        return _f, _m

    def dc_max(self, D: float) -> Tuple[float, float]:
        x1 = 0.0
        dx_max = 0.0
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

    def __repr__(self) -> str:
        sl = "layers" if len(self.layers) > 1 else "layer"
        s = f"{self.rebar.label} in {len(self.layers)} {sl}\n"
        s += f"{'dc':>10}{'xc':>10}{'Bars':>12}{'Area':>10}\n"
        for L in sorted(self.layers):
            s += f"{L._dc:10.2f}{L._xc:10.2f}{L.bar_list():>12}{L.area:10.2f}{L.stress_type.capitalize():>15}\n"
        s += " " * 32 + "-" * 10 + "\n"
        s += f"{self.area:42.2f}\n"
        return s

    def report(
        self, xu: float, conc: Concrete, rebar: Rebar, ecmax: float
    ) -> List[Dict[str, Union[str, int, float]]]:  # pragma: no cover
        result = []
        for L in sorted(self.layers):
            result.append(L.report(xu, conc, rebar, ecmax))
        return result


"""Shear reinforcement"""


class ShearReinforcement(ABC):  # pragma: no cover
    def __init__(self, rebar: Rebar, _Asv: float = 0.0, _sv: float = 0.0):
        self.rebar = rebar
        self.__Asv = _Asv
        self._sv = _sv

    @abstractmethod
    def _Asv(self):
        pass

    @abstractmethod
    def Vus(self, d: float) -> float:
        pass

    @abstractmethod
    def get_type(self):
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
        super().__init__(rebar, _nlegs * pi * _bar_dia ** 2 / 4, _sv)
        self._nlegs = _nlegs
        self._bar_dia = _bar_dia
        self._alpha_deg = _alpha_deg

    def _Asv(self) -> float:
        self.__Asv = self.nlegs * pi * self.bar_dia ** 2 / 4
        return self.__Asv

    @property
    def Asv(self):
        return self._Asv()

    @property
    def nlegs(self) -> int:
        return self._nlegs

    @nlegs.setter
    def nlegs(self, n) -> float:
        self._nlegs = n
        self.__Asv = self.nlegs * pi * self.bar_dia ** 2 / 4
        return self.__Asv

    @property
    def bar_dia(self) -> int:
        return self._bar_dia

    @bar_dia.setter
    def bar_dia(self, dia) -> None:
        self._bar_dia = dia
        self.__Asv = self.nlegs * pi * self.bar_dia ** 2 / 4

    @property
    def sv(self) -> float:
        return self._sv

    @sv.setter
    def sv(self, _sv: float) -> float:
        self._sv = _sv
        return self._sv

    def calc_sv(self, Vus: float, d: float) -> Optional[float]:
        if (self._alpha_deg < 45) or (self._alpha_deg > 90):
            return None
        alpha_rad = self._alpha_deg * pi / 180
        self._sv = self.rebar.fd * self.Asv * d * sin(alpha_rad) / Vus
        return self._sv

    def __repr__(self) -> str:
        sh_rein = "Vertical" if self._alpha_deg == 90 else "Inclined"
        s = f"{sh_rein} Stirrups: {self.rebar.label} "
        s += f"{self._nlegs}-{self._bar_dia} @ {self._sv} c/c"
        if self._alpha_deg != 90:
            s += " inclined at {self._alpha_deg} degrees"
        s += f" (Asv = {self.Asv:.2f})"
        return s

    def Vus(self, d: float) -> float:
        Vus = self.rebar.fd * self.Asv * d / self._sv
        if self._alpha_deg != 90:
            alpha_rad = self._alpha_deg * pi / 180
            Vus *= sin(alpha_rad) + cos(alpha_rad)
        return Vus

    def get_type(self) -> int:
        if self._alpha_deg == 90:
            return ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP
        else:
            return ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP


"""Single group (sv == 0) or a series of parallel (sv != 0) bent-up bars as shear reinforcement"""


class BentupBars(ShearReinforcement):
    def __init__(
        self, rebar: Rebar, bars: List[int], _alpha_deg: float = 45, _sv: float = 0.0
    ):
        super().__init__(rebar, pi / 4 * sum([x ** 2 for x in bars]), _sv)
        self.bars = bars
        self._alpha_deg = _alpha_deg

    def _Asv(self) -> float:
        area = 0.0
        for bar_dia in self.bars:
            area += bar_dia ** 2
        self.__Asv = pi / 4 * area
        return self.__Asv

    @property
    def Asv(self):
        return self._Asv()

    def Vus(self, d: float = 0.0) -> float:
        Vus = self.rebar.fd * self.Asv
        alpha_rad = self._alpha_deg * pi / 180
        if self._sv == 0:  # Single group of parallel bars
            Vus *= sin(alpha_rad)
        else:  # Series of bars bent-up at different sections
            Vus *= d / self._sv * (sin(alpha_rad) + cos(alpha_rad))
        return Vus

    def get_type(self) -> int:
        if self._sv == 0:
            return ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE
        else:
            return ShearRebarType.SHEAR_REBAR_BENTUP_SERIES

    def __repr__(self) -> str:
        if self._sv == 0:
            s = f"Single group of parallel bent-up bars: {self.rebar.label}-[{self.bars}]"
        else:
            s = f"Series of parallel bent-up bars: {self.rebar.label}-{self.bars} @ {self._sv} c/c"
        if self._alpha_deg != 90:
            s += f" inclined at {self._alpha_deg} degrees"
        s += f" (Asv = {self.Asv:.2f})"
        return s


class ShearRebarGroup:
    def __init__(self, shear_reinforcement: List[ShearReinforcement]):
        self.shear_reinforcement = shear_reinforcement

    def Asv(self) -> List[float]:
        asv = []
        for reinf in self.shear_reinforcement:
            asv.append(reinf._Asv())
        return asv

    def Vus(self, d: float) -> List[float]:
        vus = []
        for reinf in self.shear_reinforcement:
            vus.append(reinf.Vus(d))
        return vus

    def get_type(self) -> Dict[ShearRebarType, int]:
        d = {
            ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP: 0,
            ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP: 0,
            ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE: 0,
            ShearRebarType.SHEAR_REBAR_BENTUP_SERIES: 0,
        }
        for reinf in self.shear_reinforcement:
            if reinf.get_type() == ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP:
                d[ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP] += 1
            elif reinf.get_type() == ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP:
                d[ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP] += 1
            elif reinf.get_type() == ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE:
                d[ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE] += 1
            elif reinf.get_type() == ShearRebarType.SHEAR_REBAR_BENTUP_SERIES:
                d[ShearRebarType.SHEAR_REBAR_BENTUP_SERIES] += 1
        return d

    def __repr__(self):
        s = ""
        for sh_reinf in self.shear_reinforcement:
            s += f"{sh_reinf}\n"
        return s
