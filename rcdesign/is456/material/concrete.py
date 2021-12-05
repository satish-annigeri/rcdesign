"""Class to represent concrete as defined in IS456:2000"""

from typing import Optional, Tuple
from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from sympy import symbols, integrate, nsimplify  # type: ignore

from rcdesign import ecy, ecu
from rcdesign.exceptions import RCDException


class StressBlockError(RCDException):
    def __init__(self, x1: float, x2: float):
        self.x1 = x1
        self.x2 = x2

    def __str__(self):
        return f"StressBlockError: Stress block distances ({self.x1}, {self.x2}) must be within 0 to 1"


class MaximumStrainError(RCDException):
    def __init__(self, ecmax: float, ecu: float):
        self.ecmax = ecmax
        self.ecmax = ecu

    def __str__(self):
        return "MaximumStrainError: Maximum strain exceeds permitted ultimate strain {}".format(
            self.ecmax
        )


# Generalized Stress Block
class StressBlock(ABC):  # pragma: no cover
    def __init__(self, label: str):
        self.label = label

    @abstractmethod
    def stress(self, x: float, ecmax: float) -> float:
        pass

    @abstractmethod
    def area(self, x1: float, x2: float, ecmax: float) -> float:
        pass

    @abstractmethod
    def moment(self, x1: float, x2: float, ecmax: float) -> float:
        pass


# Concrete Stress Block for flexure as per IS456:2000 Limit State Method


class ConcreteLSMFlexure(StressBlock):
    z, k = symbols("z k")
    expr = 2 * k * z - k ** 2 * z ** 2

    def __init__(self, label: str, ecy: float = ecy, ecu: float = ecu):
        super().__init__(label)
        self.ecy = ecy
        self.ecu = ecu

    def validate_sb(self, x1: float, x2: float) -> Tuple[float, float]:
        if x1 > x2:
            x1, x2 = x2, x1
        if (0 <= x1 <= 1) and (x1 <= x2 <= 1):
            return x1, x2
        raise StressBlockError(x1, x2)

    def stress(self, x: float, ecmax: float = ecu) -> float:
        if ecmax > self.ecu:
            raise MaximumStrainError(ecmax, self.ecu)
        k = nsimplify(ecmax / self.ecy)

        if x <= 1 / k:
            r = self.expr.evalf(subs={"z": x, "k": k})
        else:
            r = 1.0
        return r

    def area(self, x1: float, x2: float, ecmax: float = ecu) -> float:
        if ecmax > self.ecu:
            raise MaximumStrainError(ecmax, self.ecu)
        x1, x2 = self.validate_sb(x1, x2)
        k = nsimplify(ecmax / self.ecy)
        if 0 <= k <= 1:  # Yield strain not crossed
            return integrate(self.expr, (self.z, x1, x2)).evalf(subs={"k": k})
        xx = 1 / k
        if x2 <= xx:  # Entirely within parabolic region
            a1 = integrate(self.expr, (self.z, x1, x2)).evalf(subs={"k": k})
            a2 = 0.0
        elif x1 >= xx:  # Entirely within rectangular region
            a1 = 0.0
            a2 = integrate(1, (self.z, x1, x2))
        else:  # Partly in parabolic and rest in rectangular region
            a1 = integrate(self.expr, (self.z, x1, xx)).evalf(subs={"k": k})
            a2 = integrate(1, (self.z, xx, x2))
        return a1 + a2

    def moment(self, x1: float, x2: float, ecmax: float = ecu) -> float:
        if ecmax > self.ecu:
            raise MaximumStrainError(ecmax, self.ecu)
        x1, x2 = self.validate_sb(x1, x2)
        k = nsimplify(ecmax / self.ecy)
        if 0 <= k <= 1:  # Yield strain not crossed
            return integrate(self.expr * self.z, (self.z, x1, x2)).evalf(subs={"k": k})
        xx = 1 / k
        if x2 <= xx:
            m1 = integrate(self.expr * self.z, (self.z, x1, x2)).evalf(subs={"k": k})
            m2 = 0.0
        elif x1 >= 1 / k:
            m1 = 0.0
            m2 = integrate(self.z, (self.z, x1, x2))
        else:
            m1 = integrate(self.expr * self.z, (self.z, x1, xx)).evalf(subs={"k": k})
            m2 = integrate(self.z, (self.z, xx, x2))
        return m1 + m2


# ConcreteLSMCompression class
"""ConcreteLSMCompression class to represent stress block for axial compression with NA outside the section"""


class ConcreteLSMCompression(StressBlock):
    z, k = symbols("z k")
    _ec = z / (k - nsimplify(3 / 7))
    _fc = 2 * _ec - _ec ** 2

    def __init__(self, label: str, ecy: float = ecy, ecu: float = ecu):
        super().__init__(label)
        self.ecy = ecy
        self.ecu = ecu

    def ec(self, k: float, z: float):
        if k < 1:
            raise ValueError
        return self._ec.evalf(subs={"k": k, "z": z})

    def ecmin(self, k: float) -> float:
        return self.ec(k, k - 1)

    def ecmax(self, k: float) -> float:
        return self.ec(k, k)

    def stress(self, k: float, z: float):
        return self._fc.evalf(subs={"k": k, "z": z})

    def area(self, z1: float, z2: float, k: float):
        if k <= 1:
            raise ValueError
        if z1 > z2:
            z1, z2 = z2, z1
        if z1 < (k - 1) or (z2 > k):
            raise ValueError
        if z2 <= k - 3 / 7:  # Parabolic only
            a1 = integrate(self._fc, (self.z, z1, z2)).evalf(subs={"k": k})
            a2 = 0.0
        elif z1 >= k - 3 / 7:  # Rectangular only
            a1 = 0.0
            a2 = integrate(1, (self.z, z1, z2)).evalf(subs={"k": k})
        else:  # Partly parabolic, partly rectangular
            a1 = integrate(self._fc, (self.z, z1, k - 3 / 7)).evalf(subs={"k": k})
            a2 = integrate(1, (self.z, k - 3 / 7, z2)).evalf(subs={"k": k})
        return a1 + a2

    def moment(self, z1: float, z2: float, k: float):
        if k <= 1:
            raise ValueError
        if z1 > z2:
            z1, z2 = z2, z1
        if z1 < (k - 1) or (z2 > k):
            raise ValueError
        if z2 <= k - 3 / 7:  # Parabolic only
            m1 = integrate(self._fc * self.z, (self.z, z1, z2)).evalf(subs={"k": k})
            m2 = 0.0
        elif z1 >= k - 3 / 7:  # Rectangular only
            m1 = 0.0
            m2 = integrate(self.z, (self.z, z1, z2)).evalf(subs={"k": k})
        else:  # Partly parabolic, partly rectangular
            m1 = integrate(self._fc * self.z, (self.z, z1, k - 3 / 7)).evalf(
                subs={"k": k}
            )
            m2 = integrate(self.z, (self.z, k - 3 / 7, z2)).evalf(subs={"k": k})
        return m1 + m2


# Concrete class
"""Concrete class with stress-strain properties as defined in IS456:2000"""


class Concrete:
    def __init__(
        self,
        label: str,
        fck: float,
        stress_block: ConcreteLSMFlexure,
        gamma_m: float = 1.5,
        density: float = 25.0,
    ):
        self.label = label
        self.fck = fck
        self.stress_block = stress_block
        self.gamma_m = gamma_m
        self.density = density

    @property
    def Ec(self) -> float:
        return 5000 * np.sqrt(self.fck)

    @property
    def ecy(self) -> float:
        return self.stress_block.ecy

    @property
    def ecu(self) -> float:
        return self.stress_block.ecu

    @property
    def fd(self) -> float:
        return 0.67 * self.fck / self.gamma_m

    def fc(self, x_xu: float, fd: float = 1.0):
        if 0 <= x_xu <= 1:
            __fc = self.stress_block.stress(x_xu)
            return __fc * fd
        else:
            raise ValueError("x/xu = %.4f. Must be between 0 and 1" % (x_xu))

    def tauc_max(self):
        tauc = np.array([[15, 20, 25, 30, 35, 40], [2.5, 2.8, 3.1, 3.5, 3.7, 4.0]])
        if self.fck < 15:
            return 0.0
        elif self.fck >= tauc[0, -1]:
            return tauc[1, -1]
        else:
            for i in range(1, len(tauc)):
                if self.fck <= tauc[0, i]:
                    x1 = tauc[0, i - 1]
                    y1 = tauc[1, i - 1]
                    x2 = tauc[0, i]
                    y2 = tauc[1, i]
                    return y1 + (y2 - y1) / (x2 - x1) * (self.fck - x1)

    def tauc(self, pt) -> float:
        if pt < 0.15:
            pt = 0.15
        if pt > 3:
            pt = 3.0
        beta = max(1.0, (0.8 * self.fck) / (6.89 * pt))
        num = 0.85 * np.sqrt(0.8 * self.fck) * (np.sqrt(1 + 5 * beta) - 1)
        den = 6 * beta
        return num / den

    def __repr__(self) -> str:
        # s = f"Stress Block {self.stress_block.label} - {self.label}: "
        s = f"fck = {self.fck:.2f} N/mm^2, fd = {self.fd:.2f} N/mm^2"
        return s

    def area(self, x1_xu: float, x2_xu: float, fd: float = 1.0) -> float:
        factor = self.stress_block.area(x1_xu, x2_xu)
        return factor * fd

    def moment(self, x1_xu: float, x2_xu: float, fd: float = 1.0) -> float:
        factor = self.stress_block.moment(x1_xu, x2_xu)
        return factor * fd

    def centroid(self, x1_xu: float, x2_xu: float, fd: float = 1.0) -> float:
        m = self.moment(x1_xu, x2_xu)
        a = self.area(x1_xu, x2_xu)
        return m / a
