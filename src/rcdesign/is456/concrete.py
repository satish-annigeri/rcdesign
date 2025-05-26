from dataclasses import dataclass
from math import sqrt
import numpy as np

# Concrete class
"""Concrete class with stress-strain properties as defined in IS456:2000"""


@dataclass
class Concrete:
    """Represents Concrete material as per IS 456:2000

    Attributes:
        label (str): A label for the object
        fck (float): Characteristic strength of concrete
        gamma_m (float): Partial safety factor for material for concrete (default: 1.5)
        density (float): Density of concrete in kN per cubic metre (default: 25.0)
    """

    label: str
    fck: float
    gamma_m: float = 1.5
    density: float = 25.0

    def __repr__(self) -> str:
        """String representation of the Concrete object

        Returns:
            string: Representation of the object that will be used by print()
        """
        s = f"fck = {self.fck:.2f} N/mm^2, fd = {self.fd:.2f} N/mm^2"
        return s

    @property
    def Ec(self) -> float:
        """float: Modulus of elasticity of concrete as per IS 456:2000"""
        return 5000 * sqrt(self.fck)

    @property
    def fd(self) -> float:
        """float: Design strength of concrete as per IS 456:2000"""
        return 0.67 * self.fck / self.gamma_m

    def tauc(self, pt: float) -> float:
        """Returns permissible design shear stress in concrete as per IS 456:2000

        Args:
            pt (float): Percentage of tension reinforcement
        Returns:
            float: Permissible design shear stress for concrete
        """
        if pt < 0.15:
            pt = 0.15
        if pt > 3:
            pt = 3.0
        beta = max(1.0, (0.8 * self.fck) / (6.89 * pt))
        num = 0.85 * sqrt(0.8 * self.fck) * (sqrt(1 + 5 * beta) - 1)
        den = 6 * beta
        return num / den

    def tauc_max(self):
        """Returns maximum permissible shear stress concrete with shear reinforcement

        Returns:
            float: Maximum permissible design shear stress for concrete with shear reinforcement
        """
        tauc = np.array([[15, 20, 25, 30, 35, 40], [2.5, 2.8, 3.1, 3.5, 3.7, 4.0]])
        if self.fck < tauc[0, 0]:
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
