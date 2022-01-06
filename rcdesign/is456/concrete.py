from math import sqrt
import numpy as np

# Concrete class
"""Concrete class with stress-strain properties as defined in IS456:2000"""


class Concrete:
    def __init__(
        self,
        label: str,
        fck: float,
        gamma_m: float = 1.5,
        density: float = 25.0,
    ):
        self.label = label
        self.fck = fck
        self.gamma_m = gamma_m
        self.density = density

    def __repr__(self) -> str:
        s = f"fck = {self.fck:.2f} N/mm^2, fd = {self.fd:.2f} N/mm^2"
        return s

    @property
    def Ec(self) -> float:
        return 5000 * sqrt(self.fck)

    @property
    def fd(self) -> float:
        return 0.67 * self.fck / self.gamma_m

    def tauc(self, pt) -> float:
        if pt < 0.15:
            pt = 0.15
        if pt > 3:
            pt = 3.0
        beta = max(1.0, (0.8 * self.fck) / (6.89 * pt))
        num = 0.85 * sqrt(0.8 * self.fck) * (sqrt(1 + 5 * beta) - 1)
        den = 6 * beta
        return num / den

    def tauc_max(self):
        tauc = np.array([[15, 20, 25, 30, 35, 40], [2.5, 2.8, 3.1, 3.5, 3.7, 4.0]])
        if self.fck < 15:
            return 0.0
        elif self.fck >= tauc[0, -1]:
            return tauc[1, -1]
        else:
            for i in range(1, tauc.shape[1]):
                if self.fck <= tauc[0, i]:
                    if self.fck == tauc[0, i]:
                        return tauc[1, i]
                    else:
                        x1 = tauc[0, i - 1]
                        y1 = tauc[1, i - 1]
                        x2 = tauc[0, i]
                        y2 = tauc[1, i]
                        print(x1, x2, y1, y2)
                        return y1 + (y2 - y1) / (x2 - x1) * (self.fck - x1)
