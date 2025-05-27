"""Classes to represent reinforcement bars, layers of reinforcement bars
and groups of reinforcement layers
"""

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
    """Enumeration for different types of reinforcement bars.

    - REBAR_UNDEFINED: Undefined type of rebar
    - REBAR_MS: Mild Steel reinforcement
    - REBAR_HYSD: High Yield Strength Deformed bars
    - REBAR_CUSTOM: Custom type of rebar defined by user
    """

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
    """Enumeration for different types of stress in reinforcement bars.

    - STRESS_NEUTRAL: Neutral stress
    - STRESS_COMPRESSION: Compression stress
    - STRESS_TENSION: Tension stress
    """

    STRESS_NEUTRAL = 0
    STRESS_COMPRESSION = 1
    STRESS_TENSION = 2


StressLabel = {
    StressType.STRESS_NEUTRAL: "Neutral",
    StressType.STRESS_COMPRESSION: "Compression",
    StressType.STRESS_TENSION: "Tension",
}


class ShearRebarType(IntEnum):
    """Enumeration for different types of shear reinforcement bars.

    - SHEAR_REBAR_VERTICAL_STIRRUP: Vertical stirrup
    - SHEAR_REBAR_INCLINED_STIRRUP: Inclined stirrup
    - SHEAR_REBAR_BENTUP_SINGLE: Bent-up bars in single group
    - SHEAR_REBAR_BENTUP_SERIES: Bent-up bars in series
    """

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
    """Base class for reinforcement bars.

    Attributes:
        label (str): Label for the reinforcement bar
        fy (float): Characteristic yield strength of the reinforcement bar
        gamma_m (float): Partial safety factor for reinforcement (default: 1.15)
        density (float): Density of the reinforcement bar (default: 78.5 kg/m^3)
        Es (float): Modulus of elasticity of the reinforcement bar (default: 2e5 MPa)
        rebar_type (RebarType): Type of reinforcement bar (default: RebarType.REBAR_HYSD)
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


class RebarMS(Rebar):
    """Mild steel reinforcement bars as defined in IS456:2000 with linear stress-strain relation"""

    def __init__(self, label: str, fy: float):
        """Initialize a Mild Steel reinforcement bar with given label and yield strength.

        Args:
            label (str): Label for the reinforcement bar
            fy (float): Characteristic yield strength of the reinforcement bar
        """
        super().__init__(label, fy)
        self.rebar_type = RebarType.REBAR_MS

    def __repr__(self):
        return f"{self.label:>6}: Type={RebarLabel[self.rebar_type]} fy={self.fy} fd={self.fd:.2f}"

    def fs(self, es: float) -> float:
        """Calculate the stress in the reinforcement bar based on the strain.

        Args:
            es (float): Strain in the reinforcement bar
        Returns:
            float: Stress in the reinforcement bar
        """
        _es = abs(es)
        _esy = self.fd / self.Es

        if _es < _esy:
            return es * self.Es
        else:
            return copysign(self.fd, es)


class RebarHYSD(Rebar):
    """High Yield Strength Deformed (HYSD) reinforcement bars as defined in IS456:2000 with non-linear stress-strain relation

    Attributes:
        label (str): Label for the reinforcement bar
        fy (float): Characteristic yield strength of the reinforcement bar
        gamma_m (float): Partial safety factor for reinforcement (default: 1.15)
        density (float): Density of the reinforcement bar (default: 78.5 kN/m^3)
        Es (float): Modulus of elasticity of the reinforcement bar (default: 2e5 N/mm^2)
    """

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
        """Calculate the stress in the reinforcement bar based on the strain.

        Args:
            es (float): Strain in the reinforcement bar
        Returns:
            float: Stress in the reinforcement bar
        """
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


@dataclass
class RebarLayer:
    """Class to represent a layer of reinforcement bars.

    Attributes:
        rebar (Rebar): The type of reinforcement bar used in this layer
        dia (List[float]): List of diameters of the bars in this layer
        _dc (float): Distance from the compression edge to the centroid of the layer
    """

    rebar: Rebar
    dia: List[float] = field(default_factory=list)
    _dc: float = 0.0

    def __post_init__(self):
        self._xc: float = self._dc
        self._stress_type: StressType = StressType.STRESS_NEUTRAL

    @property
    def max_dia(self) -> float:
        """Return the maximum diameter of the bars in this layer."""
        return max(self.dia)

    @property
    def area(self) -> float:
        """Calculate the total cross-sectional area of the bars in this layer."""
        return sum([d**2 for d in self.dia]) * pi / 4

    @property
    def dc(self) -> float:
        """Return the distance from the compression edge to the centroid of the layer."""
        return self._dc

    @dc.setter
    def dc(self, _dc) -> None:
        self._dc = _dc
        if _dc >= 0:
            self._xc = _dc

    @property
    def xc(self) -> float:
        """Return the distance from the compression edge to the centroid of the layer."""
        return self._xc

    @xc.setter
    def xc(self, D: float) -> float:
        if self.dc > 0:
            self._xc = self.dc
        else:
            self._xc = D + self.dc
        return self._xc

    def stress_type(self, xu: float) -> StressType:
        """Determine the type of stress in this layer based on the distance from the compression edge to the neutral axis.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            StressType: The type of stress in this layer (STRESS_NEUTRAL, STRESS_COMPRESSION, or STRESS_TENSION)
        """
        if isclose(self._xc, xu):
            self._stress_type = StressType.STRESS_NEUTRAL
        elif self._xc < xu:
            self._stress_type = StressType.STRESS_COMPRESSION
        elif self._xc > 0:
            self._stress_type = StressType.STRESS_TENSION
        return self._stress_type

    def x(self, xu: float) -> float:
        """Calculate the distance from the compression edge to the centroid of the layer based on the distance from the compression edge to the neutral axis.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            float: The distance from the compression edge to the centroid of the layer
        """
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
        """Calculate the strain in the reinforcement bar based on the distance from the compression edge to the neutral axis.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            float: The strain in the reinforcement bar
        """
        return ecmax / xu * self.x(xu)

    def fs(self, xu: float, ecmax: float = ecu) -> float:
        """Calculate the stress in the reinforcement bar based on the distance from the compression edge to the neutral axis.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            float: The stress in the reinforcement bar
        """
        return self.rebar.fs(self.es(xu, ecmax))

    def force_compression(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float = ecu,
    ) -> Tuple[float, float, Dict]:
        """Calculate the force and moment in the compression reinforcement.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            csb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Tuple[float, float, Dict]: A tuple containing the force in the compression reinforcement,
            the moment about the neutral axis, and a dictionary with detailed results.
        """
        x = self.x(xu)
        esc = self.es(xu, ecmax)
        fsc = self.rebar.fs(esc)  # Stress in compression steel
        fcc = conc.fd * csb._fc_(esc)  # Stress in concrete
        _f = self.area * (fsc - fcc)
        _m = _f * x
        result = {"x": x, "esc": esc, "f_s": fsc, "f_c": fcc, "C": _f, "M": _m}
        return _f, _m, result

    def force_tension(self, xu: float, ecmax: float = ecu) -> Tuple[float, float, Dict]:
        """Calculate the force and moment in the tension reinforcement.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Tuple[float, float, Dict]: A tuple containing the force in the tension reinforcement,
            the moment about the neutral axis, and a dictionary with detailed results.
        """
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
        """Generate a report for the reinforcement layer.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            csb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            rebar (Rebar): The type of reinforcement bar used in this layer
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Dict[str, Any]: A dictionary containing detailed results of the reinforcement layer
        """
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
        """Generate a string representation of the bars in this layer.

        Args:
            sep (str): Separator to use between different bar diameters (default: ";")
        Returns:
            str: A string representation of the bars in this layer, showing the count and diameter.
        """
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
        """Calculate the spacing between the bars in this layer based on the total width and clear cover.

        Args:
            b (float): Total width available for the bars in this layer
            clear_cover (float): Clear cover distance from the edge of the concrete to the nearest bar
        Returns:
            float: The spacing between the bars in this layer
        """
        return (b - (2 * clear_cover) - sum(self.dia)) / (len(self.dia) - 1)

    def asdict(self, xu: float, sb: LSMStressBlock, conc: Concrete, ecmax: float = ecu) -> dict:  # pragma: no cover
        """Generate a dictionary representation of the reinforcement layer.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            sb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            dict: A dictionary containing detailed results of the reinforcement layer
        """
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


@dataclass
class RebarGroup:
    """Class to represent a group of reinforcement layers.

    Attributes:
        layers (List[RebarLayer]): List of layers of bars, in no particular order, of distance from compression edge
    """

    layers: List[RebarLayer] = field(
        default_factory=list
    )  # List of layers of bars, in no particular order, of distance from compression edge

    @property
    def area(self) -> float:
        """Calculate the total cross-sectional area of all layers in the group."""
        return sum([L.area for L in self.layers])

    def calc_xc(self, D: float) -> None:
        """Calculate the distance from the compression edge to the centroid of each layer in the group.

        Args:
            D (float): Total depth of the section from the compression edge to the centroid of the reinforcement
        Returns:
            None: This method modifies the xc attribute of each layer in the group.
        """
        for L in self.layers:
            L.xc = D
        return None

    def centroid(self, xu: float) -> Tuple[float, float]:
        """Calculate the centroids of the compression and tension reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            Tuple[float, float]: A tuple containing the centroid of the compression reinforcement and the centroid of the tension reinforcement
        """
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
        """Check if there is any compression reinforcement in the group.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            bool: True if there is compression reinforcement in the group, False otherwise
        """
        for L in self.layers:
            if L._xc < xu:
                return True
        return False

    def Asc(self, xu: float) -> float:
        """Calculate the total cross-sectional area of compression reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            float: The total cross-sectional area of compression reinforcement layers
        """
        a = 0.0
        for L in self.layers:
            if L._xc < xu:
                a += L.area
        return a

    def Ast(self, xu: float) -> float:
        """Calculate the total cross-sectional area of tension reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            float: The total cross-sectional area of tension reinforcement layers
        """
        a = 0.0
        for L in self.layers:
            if L._xc > xu:
                a += L.area
        return a

    def get_stress_type(self, xu: float) -> None:
        """Set the stress type for each layer based on the distance from the compression edge to the neutral axis.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
        Returns:
            None: This method modifies the _stress_type attribute of each layer in the group.
        """
        for L in self.layers:
            L.stress_type(xu)

    def force_moment(
        self,
        xu: float,
        csb: LSMStressBlock,
        conc: Concrete,
        ecmax: float = ecu,
    ) -> Tuple[float, float, float, float]:
        """Calculate the forces and moments in the reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            csb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Tuple[float, float, float, float]: A tuple containing the force and moment in compression reinforcement,
            the force and moment in tension reinforcement
        """
        fc, mc = self.force_compression(xu, csb, conc, ecmax)
        ft, mt = self.force_tension(xu, ecmax)
        return fc, mc, ft, mt

    def force_tension(self, xu: float, ecmax: float = ecu) -> Tuple[float, float]:
        """Calculate the force and moment in the tension reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Tuple[float, float]: A tuple containing the total force and moment in the tension reinforcement layers
        """
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
        """Calculate the force and moment in the compression reinforcement layers.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            csb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            Tuple[float, float]: A tuple containing the total force and moment in the compression reinforcement layers
        """
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
        """Generate a report for the reinforcement group.

        Args:
            xu (float): Distance from the compression edge to the neutral axis
            csb (LSMStressBlock): Concrete stress block
            conc (Concrete): Concrete properties
            ecmax (float): Maximum strain in the concrete (default: ecu)
        Returns:
            List[Dict[str, Union[str, int, float]]]: A list of dictionaries containing detailed results for each layer in the group
        """
        result = []
        for L in sorted(self.layers):
            result.append(L.report(xu, csb, conc, L.rebar, ecmax))
        return result


@dataclass
class ShearReinforcement(ABC):  # pragma: no cover
    """Base class for shear reinforcement.

    Attributes:
        rebar (Rebar): The type of reinforcement bar used for shear reinforcement
        _Asv_ (float): Area of shear reinforcement per unit length
        _sv (float): Spacing of shear reinforcement
    """

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


class Stirrups(ShearReinforcement):
    """Class to represent vertical or inclined stirrups as shear reinforcement.
    This class is used to calculate the area of shear reinforcement, spacing, and shear capacity.
    It can handle both vertical and inclined stirrups with specified number of legs and bar diameter.

    Attributes:
        rebar (Rebar): The type of reinforcement bar used for stirrups
        _nlegs (int): Number of legs in the stirrup
        _bar_dia (float): Diameter of the stirrup bar
        _sv (float): Spacing of the stirrup
        _alpha_deg (float): Angle of inclination of the stirrup in degrees (default: 90 for vertical stirrups)
    """

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
        """Calculate the area of shear reinforcement per unit length."""

        return self.nlegs * pi * self.bar_dia**2 / 4

    @property
    def Asv(self):
        """Return the area of shear reinforcement per unit length."""
        return self.nlegs * pi * self.bar_dia**2 / 4

    @property
    def nlegs(self) -> int:
        """Return the number of legs in the stirrup."""
        return self._nlegs

    @nlegs.setter
    def nlegs(self, n) -> float:
        self._nlegs = n
        return self._nlegs

    @property
    def bar_dia(self) -> float:
        """Return the diameter of the stirrup bar."""
        return self._bar_dia

    @bar_dia.setter
    def bar_dia(self, dia) -> float:
        self._bar_dia = dia
        return self._bar_dia

    @property
    def sv(self) -> float:
        """Return the spacing of the stirrup."""
        return self._sv

    @sv.setter
    def sv(self, _sv: float) -> float:
        self._sv = _sv
        return self._sv

    def calc_sv(self, Vus: float, d: float) -> Optional[float]:
        """Calculate the spacing of the stirrup based on the shear force and effective depth.

        Args:
            Vus (float): Shear force to be resisted by the stirrup
            d (float): Effective depth of the section
        Returns:
            Optional[float]: The calculated spacing of the stirrup, or None if the spacing is not set
        """
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
        """Calculate the shear capacity provided by the stirrup based on the effective depth.

        Args:
            d (float): Effective depth of the section
        Returns:
            float: The shear capacity provided by the stirrup
        """
        alpha_rad = deg2rad(self._alpha_deg)
        sind = sin(alpha_rad)
        cosd = cos(alpha_rad)
        V_us = self.rebar.fd * self.Asv * d / self._sv * (sind + cosd)
        return V_us

    def get_type(self) -> int:
        """Return the type of shear reinforcement based on the angle of inclination."""
        if self._alpha_deg == 90:
            return ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP
        else:
            return ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP

    def report(self, d: float) -> dict:
        """Generate a report for the stirrup reinforcement.

        Args:
            d (float): Effective depth of the section
        Returns:
            dict: A dictionary containing detailed results of the stirrup reinforcement
        """
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


class BentupBars(ShearReinforcement):
    """Class to represent a single group of bent-up bars as shear reinforcement.

    This class is used to calculate the area of shear reinforcement, spacing, and shear capacity for bent-up bars.
    It can handle both single groups of parallel bars and series of bars bent-up at different sections.

    Attributes:
        rebar (Rebar): The type of reinforcement bar used for bent-up bars
        bars (List[int]): List of diameters of the bent-up bars
        _alpha_deg (float): Angle of inclination of the bent-up bars in degrees (default: 45)
        _sv (float): Spacing of the bent-up bars (default: 0.0, indicating a single group of parallel bars)
    """

    def __init__(self, rebar: Rebar, bars: List[int], _alpha_deg: float = 45, _sv: float = 0.0):
        super().__init__(rebar)
        self.bars = bars
        self._alpha_deg = _alpha_deg
        self._Asv_ = pi / 4 * sum([x**2 for x in bars])
        self._sv = _sv

    def _Asv(self) -> float:
        """Calculate the area of shear reinforcement per unit length for bent-up bars."""
        area = 0.0
        for bar_dia in self.bars:
            area += bar_dia**2
        self._Asv_ = pi / 4 * area
        return self._Asv_

    @property
    def Asv(self) -> float:
        """Return the area of shear reinforcement per unit length for bent-up bars."""
        return self._Asv()

    def Vus(self, d: float = 0.0) -> float:
        """Calculate the shear capacity provided by the bent-up bars based on the effective depth.

        Args:
            d (float): Effective depth of the section (default: 0.0)
        Returns:
            float: The shear capacity provided by the bent-up bars
        """
        V_us = self.rebar.fd * self.Asv
        alpha_rad = deg2rad(self._alpha_deg)
        if self._sv == 0:  # Single group of parallel bars
            V_us *= sin(alpha_rad)
        else:  # Series of bars bent-up at different sections
            V_us *= d / self._sv * (sin(alpha_rad) + cos(alpha_rad))
        return V_us

    def get_type(self) -> int:
        """Return the type of shear reinforcement based on the spacing of the bent-up bars."""
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
        """Generate a report for the bent-up bars reinforcement.

        Args:
            d (float): Effective depth of the section
        Returns:
            dict: A dictionary containing detailed results of the bent-up bars reinforcement
        """
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
    """Class to represent a group of shear reinforcement.

    This class is used to manage multiple shear reinforcement elements, such as stirrups and bent-up bars.
    It provides methods to calculate the total area of shear reinforcement, shear capacity, and check the type of reinforcement.

    Attributes:
        shear_reinforcement (List[ShearReinforcement]): List of shear reinforcement elements (stirrups, bent-up bars, etc.)
    """

    def __init__(self, shear_reinforcement: List[ShearReinforcement]):
        self.shear_reinforcement = shear_reinforcement.copy()

    def _Asv(self) -> List[float]:
        """Calculate the area of shear reinforcement for each element in the group.

        Returns:
            List[float]: A list containing the area of shear reinforcement for each element in the group
        """
        asv = []
        for reinf in self.shear_reinforcement:
            asv.append(reinf._Asv())
        return asv

    @property
    def Asv(self) -> List[float]:
        """Return the area of shear reinforcement for each element in the group."""
        return self._Asv()

    def Vus(self, d: float) -> List[float]:
        """Calculate the shear capacity provided by each element in the group based on the effective depth.

        Args:
            d (float): Effective depth of the section
        Returns:
            List[float]: A list containing the shear capacity provided by each element in the group
        """
        vus = []
        for reinf in self.shear_reinforcement:
            vus.append(reinf.Vus(d))
        return vus

    def get_type(self) -> Dict[ShearRebarType, int]:
        """Get the count of each type of shear reinforcement in the group.

        Returns:
            Dict[ShearRebarType, int]: A dictionary with the count of each type of shear reinforcement
        """
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
        """Check if the shear reinforcement is sufficient based on the type and count of reinforcement.

        Returns:
            bool: True if the shear reinforcement is sufficient, False otherwise
        """
        d = self.get_type()
        print("***", d)
        if (
            (d[ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP] < 2)
            and (d[ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP] < 2)
            and (d[ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE] < 2)
            and (d[ShearRebarType.SHEAR_REBAR_BENTUP_SERIES] < 2)
        ):
            return True
        else:
            return False

    def __repr__(self):
        s = ""
        for sh_reinf in self.shear_reinforcement:
            s += f"{sh_reinf}\n"
        return s


@dataclass
class LateralTie:
    """Class to represent lateral ties in reinforced concrete columns.

    Attributes:
        rebar (Rebar): The type of reinforcement bar used for the lateral ties
        bar_dia (int): Diameter of the lateral tie bar
        spacing (float): Spacing between the lateral ties
    """

    rebar: Rebar
    bar_dia: int
    spacing: float

    def __repr__(self):
        s = f"Lateral Ties: {self.rebar} - {self.bar_dia} @ {self.spacing:.0f}"
        return s
