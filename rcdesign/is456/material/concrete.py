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
    def stress(self, x: float):
        pass

    @abstractmethod
    def area(self, x1: float, x2: float):
        pass

    @abstractmethod
    def moment(self, x1: float, x2: float):
        pass


# Concrete Stress Block for flexure as per IS456:2000 Limit State Method


class ConcreteLSMFlexure(StressBlock):
    z = symbols("z")
    expr = 2 * z - z ** 2

    def __init__(self, label):
        super().__init__(label)
        self.ecy = ecy
        self.ecu = ecu

    def validate_sb(self, x1: float, x2: float) -> Tuple[float, float]:
        if x1 > x2:
            x1, x2 = x2, x1
        if (0 <= x1 <= 1) and (x1 <= x2 <= 1):
            return x1, x2
        raise StressBlockError(x1, x2)

    def stress(self, x: float, ecmax: float = 0.0035) -> float:
        if ecmax > self.ecu:
            raise MaximumStrainError(ecmax, self.ecu)
        k = self.ecy / ecmax

        if x <= k:
            r = self.expr.evalf(subs={"z": x / k})
        else:
            r = 1.0
        return r

    def area(self, x1: float, x2: float, ecmax: float = 0.0035) -> float:
        x1, x2 = self.validate_sb(
            x1, x2
        )  # Throws an exception if x1 and x2 are invalid
        k = nsimplify(self.ecy / ecmax)

        if x2 <= k:  # Entirely within parabolic region
            a1 = integrate(self.expr, (self.z, x1 / k, x2 / k)) * k
            a2 = 0.0
        elif x1 >= k:  # Entirely within rectangular region
            a1 = 0.0
            a2 = integrate(1, (self.z, x1, x2))
        else:  # Partly in parabolic and rest in rectangular region
            a1 = integrate(self.expr, (self.z, x1 / k, 1)) * k
            a2 = integrate(1, (self.z, k, x2))
        return a1 + a2

    def moment(self, x1: float, x2: float, ecmax: float = 0.0035) -> float:
        x1, x2 = self.validate_sb(
            x1, x2
        )  # Throws an exception if x1 and x2 are invalid
        k = nsimplify(self.ecy / ecmax)

        if x2 <= k:
            m1 = integrate(self.expr * self.z, (self.z, x1 / k, x2 / k)) * k ** 2
            m2 = 0.0
        elif x1 >= k:
            m1 = 0.0
            m2 = integrate(self.z, (self.z, x1, x2))
        else:
            m1 = integrate(self.expr * self.z, (self.z, x1 / k, 1)) * k ** 2
            m2 = integrate(self.z, (self.z, k, x2))
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
        s = f"Stress Block {self.stress_block.label} - {self.label}: "
        s += f"fck = {self.fck:.2f} N/mm^2, fd = {self.fd:.2f} N/mm^2"
        return s
