"""Class to represent concrete as defined in IS456:2000"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from sympy import symbols, integrate, nsimplify


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
@dataclass
class ConcreteStressBlock(StressBlock):
    z = symbols("z")
    expr = 2 * z - z ** 2

    def __init__(self, label, ecy: float, ecu: float):
        super().__init__(label)
        self.ecy = ecy
        self.ecu = ecu

    def invalidx(self, x1: float, x2: float = 1) -> bool:
        if x1 > x2:
            x1, x2 = x2, x1
        return not ((0 <= x1 <= 1) and (0 <= x2 <= 1))

    def stress(self, x: float, ecmax: float = 0.0035) -> float:
        k = self.ecy / ecmax

        if x <= k:
            r = self.expr.evalf(subs={"z": x / k})
        else:
            r = 1.0
        return r

    def area(self, x1: float, x2: float, ecmax: float = 0.0035) -> float:
        if self.invalidx(x1, x2):
            return None
        if x1 > x2:
            x1, x2 = x2, x1
        k = nsimplify(self.ecy / ecmax)

        if x2 <= k:
            a1 = integrate(self.expr, (self.z, x1 / k, x2 / k)) * k
            a2 = 0.0
        elif x1 >= k:
            a1 = 0.0
            a2 = integrate(1, (self.z, x1, x2))
        else:
            a1 = integrate(self.expr, (self.z, x1 / k, 1)) * k
            a2 = integrate(1, (self.z, k, x2))
        return a1 + a2

    def moment(self, x1: float, x2: float, ecmax: float = 0.0035) -> float:
        if self.invalidx(x1, x2):
            return
        if x1 > x2:
            x1, x2 = x2, x1
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


@dataclass
class Concrete:
    label: str
    fck: float
    stress_block: ConcreteStressBlock
    gamma_m: float = 1.5
    density: float = 25.0

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
        if factor:
            return factor * fd
        else:
            return None

    def moment(self, x1_xu: float, x2_xu: float, fd: float = 1.0) -> float:
        factor = self.stress_block.moment(x1_xu, x2_xu)
        if factor:
            return factor * fd
        else:
            return None

    def centroid(self, x1_xu: float, x2_xu: float, fd: float = 1.0) -> float:
        return self.moment(x1_xu, x2_xu) / self.area(x1_xu, x2_xu)

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

    def __repr__(self) -> str:  # pragma: no cover
        s = f"Stress Block {self.stress_block.label} - {self.label}: "
        s += f"{self.fck} {self.fd:.2f} {self.density}"
        return s
