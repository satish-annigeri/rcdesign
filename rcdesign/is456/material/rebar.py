""" Classes to represent reinforcement bars, layers of reinforcement bars and groups of reinforcement layers"""

from typing import List
from dataclasses import dataclass
from abc import ABC, abstractmethod

import numpy as np
from numpy import pi

from .concrete import ConcreteStressBlock, Concrete

# Rebar class

@dataclass
class Rebar(ABC):
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

"""Mild steel reinforcement bars as defined in IS456:2000 with a well defined yield point"""
class RebarMS(Rebar):
    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)

    def __repr__(self):
        return f"{self.label:>6}: Type={'MS':4} fy={self.fy} fd={self.fd:.2f}"

    def _fs(self, es: float):
        _es = abs(es)
        _esy = self.fd / self.Es

        if _es < _esy:
            return es * self.Es
        else:
            return self.fd

    def fs(self, es: float):
        if isinstance(es, np.ndarray):
            return np.array([self._fs(x) for x in es])
        else:
            return self._fs(es)


"""High yield strength deformed bars as defined in IS456:2000 with piece-wise linear stress-strain relation
between 0.8 to 1.0 times design strength"""
class RebarHYSD(Rebar):
    inel = np.array([
            [   0.8,   0.85,    0.9,  0.95, 0.975, 1.0],
            [   0.0, 0.0001, 0.0003, 0.0007, 0.001, 0.002]
    ]).T
    def __init__(self, label: str, fy: float):
        super().__init__(label, fy)
        self.es = RebarHYSD.inel.copy()
        self.es[:,0] = self.es[:,0] * self.fy / self.gamma_m
        self.es[:,1] = self.es[:,0] / self.Es + self.es[:,1]

    def __repr__(self):
        return f"{self.label:>6}: Type={'HYSD'} fy={self.fy} fd={self.fd:.2f}"

    def _fs(self, es: float):
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

    def fs(self, es: float):
        if isinstance(es, np.ndarray):
            return np.array([self._fs(x) for x in es])
        else:
            return self._fs(es)


"""Layer of reinforcement bars"""
@dataclass
class RebarLayer:
    _dc: float        # Distance of centre of layer from edge of section
    dia: List[int]    # List of bar diameters, from left to right, all of the same type to be defined in RebarGroup

    def max_dia(self):
        return max(self.dia)

    def area(self):
        return sum([pi * d**2 / 4 for d in self.dia])

    @property
    def dc(self):
        return self._dc

    def x(self, xu: float):
        return xu - self._dc

    def __repr__(self):
        s = "Dia: "
        b = ''
        for bardia in self.dia:
            b += f"{bardia}, "
        b = '[' + b[:-2] + ']'
        s += f"{b} at {self.dc}. Area: {self.area():.2f}"
        return s

    def fs(self, xu: float, rebar: Rebar, ecu:float):
        es = ecu / xu * self.x(xu)
        return rebar._fs(es)

    def force_tension(self, xu: float, D_xu: float, rebar: Rebar, ecu: float):
        x = D_xu - self._dc
        es = ecu / xu * x
        fs = rebar.fs(es)
        
        _f = self.area() * fs
        _m = _f * x
        return _f, _m

    def force_compression(self, xu: float, conc: Concrete, rebar: Rebar, ecu: float):
        x = xu - self._dc
        esc = ecu / xu * x
        fsc = rebar._fs(esc)           # Stress in compression steel
        fcc = conc.fc(x / xu, conc.fd) # Stress in concrete
        print('===', esc, fsc, fcc)
        _f = self.area() * (fsc - fcc)
        _m = _f * x
        return _f, _m


"""Group of reinforcement bars"""
@dataclass
class RebarGroup:
    rebar: Rebar              # Rebar object
    layers: List[RebarLayer]  # Layers each with its own dc and list of bar diameters

    def area(self):
        return sum([layer.area() for layer in self.layers])

    def _dc(self):
        a = 0
        m = 0
        for layer in self.layers:
            _a = layer.area()
            a += _a
            m += _a * layer.dc
        return (m / a)

    @property
    def dc(self):
        return self._dc()

    def __repr__(self):
        sl = 'layers' if len(self.layers) > 1 else 'layer'
        s = f"Rebar Group {self.rebar.label} in {len(self.layers)} {sl}\n"
        for layer in self.layers:
            s += '\t' + layer.__repr__() + '\n'
        s += f"\tTotal Area: {self.area():.2f} at {self.dc:.2f}"
        return s

    def force_tension(self, xu: float, D_xu: float, ecu:float):
        _f = 0.0
        _m = 0.0
        for layer in self.layers:
            __f, __m = layer.force_tension(xu, D_xu, self.rebar, ecu)
            _f += __f
            _m += __m
        return _f, _m

    def force_compression(self, xu: float, conc: Concrete, ecu: float):
        _f = 0.0
        _m = 0.0
        for layer in self.layers:
            __f, __m = layer.force_compression(xu, conc, self.rebar, ecu)
            _f += __f
            _m += __m
        return _f, _m


class ShearReinforcement(ABC):
    @abstractmethod
    def Asv(self):
        pass

    @abstractmethod
    def sv(self):
        pass


"""Vertical or inclined stirrups as shear reinforcement"""
@dataclass
class Stirrups(ShearReinforcement):
    rebar: Rebar
    _nlegs: int
    _bar_dia: int
    _alpha_deg: float = 90
    _sv: float = 0.0
    _Asv: float = 0.0

    @property
    def Asv(self):
        self._Asv = self.nlegs * pi * self.bar_dia**2 / 4
        return self._Asv

    @property
    def nlegs(self):
        return self._nlegs

    @nlegs.setter
    def nlegs(self, n):
        self._nlegs = n
        self._Asv = self.nlegs * pi * self.bar_dia**2 / 4

    @property
    def bar_dia(self):
        return self._bar_dia

    @bar_dia.setter
    def bar_dia(self, dia):
        self._bar_dia = dia
        self._Asv = self.nlegs * pi * self.bar_dia**2 / 4

    def sv(self, Vus: float, d: float):
        if (self._alpha_deg < 45) or (self._alpha_deg > 90):
            return
        alpha_rad = self._alpha_deg * pi / 180
        self._sv = self.rebar.fd * self.Asv * d * np.sin(alpha_rad) / Vus
        return self._sv


"""Bent up bars as shear reinforcement"""
class BentupBars(Stirrups):
    def __init__(self, rebar: Rebar, bars: List[int], alpha_deg: float):
        super().__init__(rebar, 0, 0, alpha_deg)
        self.bars = bars

    @property
    def Asv(self):
        area = 0.0
        for bar_dia in self.bars:
            area += bar_dia**2
        return np.pi * area / 4


# if __name__ == '__main__':
#     # Test RebarMS and RebarHYSD

#     ms = RebarMS('MS 250', 250)
#     print(f"{ms} {ms.fs(0.001):.2f}")

#     fe415 = RebarHYSD('Fe 415', 415)
#     print(f"{fe415} {fe415.fs(0.002):.2f}")
#     print(fe415.es)
#     print(fe415.fs(0.8*415/1.15/2e5 + 1e-6))

#     fe500 = RebarHYSD('Fe 500', 500)
#     print(f"{fe500} {fe500.fs(0.002):.2f}")

#     # Test RebarLayer

#     t1 = RebarLayer(35, [16, 16, 16])
#     t2 = RebarLayer(70, [16, 16])
#     c1 = RebarLayer(35, [16, 16])
#     print(t1)
#     print(t2)
#     print(c1)

#     is456_lsm = ConcreteStressBlock('IS456:2000 LSM', 0.002, 0.0035)
#     fe415 = RebarHYSD('Fe 415', 415)
#     m20 = Concrete('M20', 20, is456_lsm)
#     D = 450
#     xu = 131.8722
#     print('   Concrete:', m20.area(0, 1, m20.fd)*xu*230)
#     print('Compression:', c1.force_compression(xu, m20, fe415, 0.0035))
#     print('    Tension:', t1.force_tension(xu, D - xu, fe415, 0.0035))
#     print('    Tension:', t2.force_tension(xu, D - xu, fe415, 0.0035))

#     t1 = RebarLayer(35, [16, 16, 16])
#     t2 = RebarLayer(70, [16, 16])
#     c1 = RebarLayer(35, [16, 16])
#     t_st = RebarGroup(fe415, [t1, t2])
#     print(t_st)
#     print(t_st.area(), t_st._dc())
#     xu = 131.8722
#     D = 450
#     print(t_st.force_tension(xu, D, 0.0035))

#     c_st = RebarGroup(fe415, [c1])
#     print(c_st)
#     print(c_st.force_compression(xu, m20, 0.0035))