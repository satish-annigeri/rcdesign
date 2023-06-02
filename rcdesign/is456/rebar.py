"""Classes to represent reinforcement bars, layers of reinforcement bars
and groups of reinforcement layers"""

from dataclasses import dataclass, field
from enum import IntEnum
from math import pi, sin, cos, isclose, copysign

from typing import Tuple, List, Union, Dict, Optional, Any
import numpy.typing as npt

from abc import ABC, abstractmethod
import numpy as np

from rcdesign.is456 import ecu
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.utils import deg2rad


# Rebar Enumerations


class RebarType(IntEnum):
    REBAR_UNDEFINED = 0
    REBAR_MS = 1
    REBAR_HYSD = 2
    REBAR_CUSTOM = 3


RebarLabel = {
    RebarType.REBAR_UNDEFINED: "Undefined",
    RebarType.REBAR_MS: "Mild Steel",
    RebarType.REBAR_HYSD: "HYSD",
    RebarType.REBAR_CUSTOM: "Custom type",
}


class StressType(IntEnum):
    STRESS_NEUTRAL = 0
    STRESS_COMPRESSION = 1
    STRESS_TENSION = 2


StressLabel = {
    StressType.STRESS_NEUTRAL: "Neutral",
    StressType.STRESS_COMPRESSION: "Compression",
    StressType.STRESS_TENSION: "Tension",
}


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


@dataclass
class Rebar(ABC):  # pragma: no cover
    """Rebar object represents a reinforcment bar.

    Parameters
    ----------
    ABC : _type_
        _description_

    Returns
    -------
    Rebar
        _description_
    """
    label: str
    fy: float
    gamma_m: float = 1.15
    density: float = 78.5
    Es: float = 2e5
    rebar_type: RebarType = RebarType.REBAR_HYSD

    @property
    def fd(self) -> float:
        return self.fy / self.gamma_m

    def es_min(self) -> float:
        return self.fd / self.Es + 0.002

    @abstractmethod
    def fs(self, es: float) -> float:
        pass


"""Mild steel reinforcement bars as defined in IS456:2000 with a
well defined yield point"""


class RebarMS(Rebar):
    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)
        self.rebar_type = RebarType.REBAR_MS

    def __repr__(self):
        return f"{self.label:>6}: Type={RebarLabel[self.rebar_type]} fy={self.fy} fd={self.fd:.2f}"

    def fs(self, es: float) -> float:
        _es = abs(es)
        _esy = self.fd / self.Es

        if _es < _esy:
            return es * self.Es
        else:
            return copysign(self.fd, es)


"""High yield strength deformed bars as defined in IS456:2000 with piece-wise
linear stress-strain relation between 0.8 to 1.0 times design strength"""


class RebarHYSD(Rebar):
    inel: npt.NDArray[np.float64] = np.array(
        [
            [0.8, 0.85, 0.9, 0.95, 0.975, 1.0],
            [0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002],
        ]
    ).T

    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)
        self.rebar_type = RebarType.REBAR_HYSD
        self.es = RebarHYSD.inel.copy()
        self.es[:, 0] = self.es[:, 0] * self.fy / self.gamma_m
        self.es[:, 1] = self.es[:, 0] / self.Es + self.es[:, 1]

    def __repr__(self) -> str:
        return f"{self.label:>6}: Type={RebarLabel[self.rebar_type]} fy={self.fy} fd={self.fd:.2f}"

    def fs(self, es: float) -> float:
        x = abs(es)
        if x < self.es[0, 1]:
            return es * self.Es
        if x > self.es[-1, 1]:
            return self.es[-1, 0]
        i1 = np.searchsorted(self.es[:, 1], x) - 1
        i2 = i1 + 1
        y1, x1 = self.es[i1]
        y2, x2 = self.es[i2]
        m = (y2 - y1) / (x2 - x1)
        y = y1 + m * (x - x1)
        return copysign(y, es)


"""Layer of reinforcement bars"""


@dataclass
class RebarLayer:
    rebar: Rebar
    dia: List[float] = field(default_factory=list)
    _dc: float = 0.0

    def __post_init__(self):
        self._xc: float = self._dc
        self._stress_type: StressType = StressType.STRESS_NEUTRAL

    @property
    def max_dia(self) -> float:
        return max(self.dia)

    @property
    def area(self) -> float:
        return sum([d**2 for d in self.dia]) * pi / 4

    @property
    def dc(self) -> float:
        return self._dc

    @dc.setter
    def dc(self, _dc) -> None:
        self._dc = _dc
        if _dc >= 0:
            self._xc = _dc

    @property
    def xc(self) -> float:
        return self._xc

    @xc.setter
    def xc(self, D: float) -> float:
        if self.dc > 0:
            self._xc = self.dc
        else:
            self._xc = D + self.dc
        return self._xc

    def stress_type(self, xu: float) -> StressType:
        if isclose(self._xc, xu):
            self._stress_type = StressType.STRESS_NEUTRAL
        elif self._xc < xu:
            self._stress_type = StressType.STRESS_COMPRESSION
        elif self._xc > 0:
            self._stress_type = StressType.STRESS_TENSION
        return self._stress_type

    def x(self, xu: float) -> float:
        return xu - self._xc

    def __repr__(self) -> str:
        s = "Dia: "
        b = ""
        for bardia in self.dia:
            b += f"{bardia:.0f}, "
        b = "[" + b[:-2] + "]"
        s += f"{b} at {self.dc}. Area: {self.area:.2f} (xc = {self._xc:.2f})"
        return s

    def es(self, xu: float, ecmax: float = ecu) -> float:
        return ecmax / xu * self.x(xu)

    def fs(self, xu: float, ecmax: float = ecu) -> float:
        return self.rebar.fs(self.es(xu, ecmax))

    def force_compression(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float = ecu,
    ) -> Tuple[float, float, Dict]:
        x = self.x(xu)
        esc = self.es(xu, ecmax)
        fsc = self.rebar.fs(esc)  # Stress in compression steel
        fcc = conc.fd * csb._fc_(esc)  # Stress in concrete
        _f = self.area * (fsc - fcc)
        _m = _f * x
        result = {"x": x, "esc": esc, "f_s": fsc, "f_c": fcc, "C": _f, "M": _m}
        return _f, _m, result

    def force_tension(self, xu: float, ecmax: float = ecu) -> Tuple[float, float, Dict]:
        x = abs(self.x(xu))
        est = ecmax / xu * x
        fst = self.rebar.fs(est)

        _f = self.area * fst
        _m = _f * x
        result = {"x": x, "est": est, "f_st": fst, "T": _f, "M": _m}
        return _f, _m, result

    def report(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        rebar: Rebar,
        ecmax: float = ecu,
    ) -> Dict[str, Any]:  # pragma: no cover
        x = self.x(xu)

        if x >= 0:  # Compression
            esc = ecmax / xu * x
            fsc = rebar.fs(esc)
            fcc = csb.fc(x / xu, ecmax) * conc.fd
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
        from collections import Counter

        d = Counter(self.dia)
        s = ""
        for k in sorted(d):
            s += f"{d[k]}-{k:.0f} "
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

    def spacing(self, b: float, clear_cover: float) -> float:
        return (b - (2 * clear_cover) - sum(self.dia)) / (len(self.dia) - 1)

    def asdict(
        self, xu: float, sb: LSMStressBlock, conc: Concrete, ecmax: float = ecu
    ) -> dict:  # pragma: no cover
        x = self.x(xu)
        es = ecmax / xu * x
        fsc = self.rebar.fs(es)
        fcc = sb._fc_(es) * conc.fd
        F = self.area * (fsc - fcc)
        d = {
            "fy": self.rebar.fy,
            "Bars": self.bar_list(),
            "xc": self.xc,
            "Strain": es,
            "Type": StressLabel[self.stress_type(xu)][0].capitalize(),
            "f_s": fsc,
            "f_c": fcc,
            "F": F,
            "M": F * x,
        }
        return d


"""Group of reinforcement bars"""


@dataclass
class RebarGroup:
    layers: List[RebarLayer] = field(
        default_factory=list
    )  # List of layers of bars, in no particular order, of distance from compression edge

    @property
    def area(self) -> float:
        return sum([L.area for L in self.layers])

    def calc_xc(self, D: float) -> None:
        for L in self.layers:
            L.xc = D
        return None

    def centroid(self, xu: float) -> Tuple[float, float]:
        a1 = m1 = a2 = m2 = 0.0

        for L in self.layers:
            if L.stress_type(xu) == StressType.STRESS_COMPRESSION:
                a1 += L.area
                m1 += L.area * L.xc
            elif L.stress_type(xu) == StressType.STRESS_TENSION:
                a2 += L.area
                m2 += L.area * L.xc
        x1 = x2 = 0.0
        if a1 > 0:
            x1 = m1 / a1
        if a2 > 0:
            x2 = m2 / a2
        return x1, x2

    def has_comp_steel(self, xu: float) -> bool:
        for L in self.layers:
            if L._xc < xu:
                return True
        return False

    def Asc(self, xu: float) -> float:
        a = 0.0
        for L in self.layers:
            if L._xc < xu:
                a += L.area
        return a

    def Ast(self, xu: float) -> float:
        a = 0.0
        for L in self.layers:
            if L._xc > xu:
                a += L.area
        return a

    def get_stress_type(self, xu: float) -> None:
        for L in self.layers:
            L.stress_type(xu)

    def force_moment(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float = ecu,
    ) -> Tuple[float, float, float, float]:
        fc, mc = self.force_compression(xu, csb, conc, ecmax)
        ft, mt = self.force_tension(xu, ecmax)
        return fc, mc, ft, mt

    def force_tension(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        f = m = 0.0
        for L in self.layers:
            if L._xc > xu:
                # D_xu = L._xc - xu
                _f, _m, _ = L.force_tension(xu, ecmax)
                f += _f
                m += _m
        return f, m

    def force_compression(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float = ecu,
    ) -> Tuple[float, float]:
        _f = _m = 0.0
        for L in self.layers:
            if L._xc < xu:
                __f, __m, _ = L.force_compression(xu, csb, conc, ecmax)
                _f += __f
                _m += __m
        return _f, _m

    def __repr__(self) -> str:
        sl = "layers" if len(self.layers) > 1 else "layer"
        s = f"{len(self.layers)} {sl}\n"
        s += f"{'dc':>10}{'xc':>10}{'Bars':>12}{'Area':>10}\n"
        for L in sorted(self.layers):
            s += f"{L._dc:10.2f}{L._xc:10.2f}{L.bar_list():>12}{L.area:10.2f}{StressLabel[L._stress_type].capitalize():>15}\n"
        s += " " * 32 + "-" * 10 + "\n"
        s += f"{self.area:42.2f}\n"
        return s

    def report(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float,
    ) -> List[Dict[str, Union[str, int, float]]]:  # pragma: no cover
        result = []
        for L in sorted(self.layers):
            result.append(L.report(xu, csb, conc, L.rebar, ecmax))
        return result


"""Shear reinforcement"""


@dataclass
class ShearReinforcement(ABC):  # pragma: no cover
    rebar: Rebar

    def __post_init__(self):
        self._Asv_: float = 0.0
        self._sv: float = 0.0

    @abstractmethod
    def _Asv(self) -> float:
        pass

    @abstractmethod
    def Vus(self, d: float) -> float:
        pass

    @abstractmethod
    def get_type(self):
        pass

    @abstractmethod
    def report(self, d: float) -> dict:
        pass


"""Vertical or inclined stirrups as shear reinforcement"""


class Stirrups(ShearReinforcement):
    def __init__(
        self,
        rebar: Rebar,
        _nlegs: int,
        _bar_dia: float,
        _sv: float = 0.0,
        _alpha_deg: float = 90,
    ):
        super().__init__(rebar)
        self._nlegs = _nlegs
        self._bar_dia = _bar_dia
        self._alpha_deg = _alpha_deg
        if self._alpha_deg not in [45, 90]:
            raise ValueError
        self._Asv_ = self._nlegs * pi * self._bar_dia**2 / 4
        self._sv = _sv

    def _Asv(self) -> float:
        return self.nlegs * pi * self.bar_dia**2 / 4

    @property
    def Asv(self):
        return self.nlegs * pi * self.bar_dia**2 / 4

    @property
    def nlegs(self) -> int:
        return self._nlegs

    @nlegs.setter
    def nlegs(self, n) -> float:
        self._nlegs = n
        return self._nlegs

    @property
    def bar_dia(self) -> float:
        return self._bar_dia

    @bar_dia.setter
    def bar_dia(self, dia) -> float:
        self._bar_dia = dia
        return self._bar_dia

    @property
    def sv(self) -> float:
        return self._sv

    @sv.setter
    def sv(self, _sv: float) -> float:
        self._sv = _sv
        return self._sv

    def calc_sv(self, Vus: float, d: float) -> Optional[float]:
        sind = sin(deg2rad(self._alpha_deg))
        cosd = cos(deg2rad(self._alpha_deg))
        self._sv = self.rebar.fd * self.Asv * d / Vus * (sind + cosd)
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
        alpha_rad = deg2rad(self._alpha_deg)
        sind = sin(alpha_rad)
        cosd = cos(alpha_rad)
        V_us = self.rebar.fd * self.Asv * d / self._sv * (sind + cosd)
        return V_us

    def get_type(self) -> int:
        if self._alpha_deg == 90:
            return ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP
        else:
            return ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP

    def report(self, d: float) -> dict:
        data = {
            "sh_type": self.get_type(),
            "label": "Stirrups",
            "type": "Vertical",
            "fy": self.rebar.fy,
            "bar_dia": self.bar_dia,
            "legs": self.nlegs,
            "sv": self._sv,
            "alpha": self._alpha_deg,
            "Asv": self.Asv,
            "Vus": self.Vus(d),
        }
        return data


"""Single group (sv == 0) or a series of parallel (sv != 0) bent-up bars as shear reinforcement"""


class BentupBars(ShearReinforcement):
    def __init__(
        self, rebar: Rebar, bars: List[int], _alpha_deg: float = 45, _sv: float = 0.0
    ):
        super().__init__(rebar)
        self.bars = bars
        self._alpha_deg = _alpha_deg
        self._Asv_ = pi / 4 * sum([x**2 for x in bars])
        self._sv = _sv

    def _Asv(self) -> float:
        area = 0.0
        for bar_dia in self.bars:
            area += bar_dia**2
        self._Asv_ = pi / 4 * area
        return self._Asv_

    @property
    def Asv(self) -> float:
        return self._Asv()

    def Vus(self, d: float = 0.0) -> float:
        V_us = self.rebar.fd * self.Asv
        alpha_rad = self._alpha_deg * pi / 180
        if self._sv == 0:  # Single group of parallel bars
            V_us *= sin(alpha_rad)
        else:  # Series of bars bent-up at different sections
            V_us *= d / self._sv * (sin(alpha_rad) + cos(alpha_rad))
        return V_us

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

    def report(self, d: float) -> dict:
        if self._sv == 0:
            bupbar_type = "Single group"
        else:
            bupbar_type = "Series"
        data = {
            "sh_type": self.get_type(),
            "label": "Bentup bars",
            "type": bupbar_type,
            "fy": self.rebar.fy,
            "bars": self.bars,
            "sv": self._sv,
            "alpha": self._alpha_deg,
            "Asv": self.Asv,
            "Vus": self.Vus(d),
        }
        return data


class ShearRebarGroup:
    def __init__(self, shear_reinforcement: List[ShearReinforcement]):
        self.shear_reinforcement = shear_reinforcement.copy()

    def _Asv(self) -> List[float]:
        asv = []
        for reinf in self.shear_reinforcement:
            asv.append(reinf._Asv())
        return asv

    @property
    def Asv(self) -> List[float]:
        return self._Asv()

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

    def check(self) -> bool:
        d = self.get_type()
        if d[ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP] > 1:
            return False
        return True

    def __repr__(self):
        s = ""
        for sh_reinf in self.shear_reinforcement:
            s += f"{sh_reinf}\n"
        return s


@dataclass
class LateralTie:
    rebar: Rebar
    bar_dia: int
    spacing: float

    def __repr__(self):
        s = f"Lateral Ties: {self.rebar} - {self.bar_dia} @ {self.spacing:.0f}"
        return s
