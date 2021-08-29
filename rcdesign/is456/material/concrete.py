"""Class to represent concrete as defined in IS456:2000"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
import numpy as np
from sympy import symbols, integrate, nsimplify


# Generalized Stress Block
class StressBlock(ABC):
    def __init__(self, label: str):
        self.label = label

    @abstractmethod
    def stress(x: float):
        pass

    @abstractmethod
    def area(x1: float, x2: float):
        pass

    @abstractmethod
    def moment(x1: float, x2: float):
        pass

# Concrete Stress Block for flexure as per IS456:2000 Limit State Method
@dataclass
class ConcreteStressBlock(StressBlock):
    z = symbols('z')
    expr = 2 * z - z**2

    def __init__(self, label, ecy: float, ecu: float):
        super().__init__(label)
        self.ecy = ecy
        self.ecu = ecu

    def invalidx(self, x1: float, x2: float=1):
        return not ((0 <= x1 <= 1) and (0 <= x2 <= 1) and (x1 <= x2))

    def stress(self, x: float, ecmax: float=0.0035):
        k = self.ecy / ecmax

        if x <= k:
            r = self.expr.evalf(subs={'z': x / k})
        else:
            r = 1.0
        return r

    def area(self, x1: float, x2: float, ecmax: float=0.0035):
        if (x1 < 0) or (x1 > 1) or (x2 < 0) or (x2 > 1):
            print('Error')
            return
        if x1 > x2:
            x1, x2 = x2, x1
        k = nsimplify(self.ecy / ecmax)

        if x2 <= k:
#             print('Only parabolic')
            a1 = integrate(self.expr, (self.z, x1/k, x2/k)) * k
            a2 = 0.0
        elif x1 >= k:
#             print('Only rectangular')
            a1 = 0.0
            a2 = integrate(1, (self.z, x1, x2))
        else:
#             print('Parabolic and rectangular')
            a1 = integrate(self.expr, (self.z, x1/k, 1)) * k
            a2 = integrate(1, (self.z, k, x2))
        return a1 + a2

    def moment(self, x1: float, x2: float, ecmax: float=0.0035):
        if (x1 < 0) or (x1 > 1) or (x2 < 0) or (x2 > 1):
            print('Error')
            return
        if x1 > x2:
            x1, x2 = x2, x1
        k = nsimplify(self.ecy / ecmax)

        if x2 <= k:
#             print('Only parabolic')
            m1 = integrate(self.expr * self.z, (self.z, x1/k, x2/k)) * k**2
            m2 = 0.0
        elif x1 >= k:
#             print('Only rectangular')
            m1 = 0.0
            m2 = integrate(self.z, (self.z, x1, x2))
        else:
#             print('Parabolic and rectangular')
            m1 = integrate(self.expr * self.z, (self.z, x1/k, 1)) * k**2
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
    def Ec(self):
        return 5000 * np.sqrt(self.fck)

    @property
    def ecy(self):
        return self.stress_block.ecy

    @property
    def ecu(self):
        return self.stress_block.ecu

    @property
    def fd(self):
        return 0.67 * self.fck / self.gamma_m

    def _fc(self, x_xu: float, fd:float=1.0):
        return self.stress_block.stress(x_xu) * fd

    def _area(self, x1_xu: float, x2_xu: float, fd:float=1.0) -> float:
        return self.stress_block.area(x1_xu, x2_xu) * fd

    def _moment(self, x1_xu: float, x2_xu: float, fd: float=1.0) -> float:
        return self.stress_block.moment(x1_xu, x2_xu) * fd

    def _centroid(self, x1_xu: float, x2_xu: float, fd: float=1.0) -> float:
        return self._moment(x1_xu, x2_xu) / self._area(x1_xu, x2_xu)

    def fc(self, ec: float):
        z = symbols('z')
        _fc_expr = 2*z - z**2
        if 0 <= ec <= self.ecu:
            if ec <= self.ecy:
                r = _fc_expr.evalf(subs={'z': ec / self.ecy})
            elif ec <= self.ecu:
                r = 1
            return self.fd * r
        else:
            return None

    def fc_cg(self, xu: float, x1: float, x2: float):
        area = self.fc_area(xu, x1, x2)
        moment = self.fc_moment(xu, x1, x2)
        return xu - (moment / area)

    def __repr__(self):
        return f"Stress Block {self.stress_block.label} - {self.label}: {self.fck} {self.fd:.2f} {self.density}"

if __name__ == '__main__':
    is456_lsm = ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035)
    m20 = Concrete('M20', 20, is456_lsm)
    print(m20, m20.Ec)
    print(m20.ecy / m20.ecu)
    print(m20._fc(1, m20.fd))
    print(m20._area(0, 1, m20.fd))
    print(m20._moment(0, 1, m20.fd))
    print(1 - m20._centroid(0, 1))

    is456_lsm2 = ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035)
    is456_lsm2.set_ecmax(0.0015)
    conc = Concrete('M20', 20, is456_lsm2)
    print(is456_lsm2.k)
    print(conc._area(0, 3/4))