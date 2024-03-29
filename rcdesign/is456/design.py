from math import sqrt
from typing import List
from dataclasses import dataclass


@dataclass
class LSMBeam:
    ecy = 0.002
    ecu = 0.0035
    gamma_mc = 1.5
    gamma_ms = 1.15
    Es = 2e5

    def xumax_d(self, fy: float) -> float:
        return self.ecu / (fy / self.gamma_ms / self.Es + 0.002 + self.ecu)

    def Mulim_const(self, fy: float) -> float:
        xumax_d = self.xumax_d(fy)
        k = (17 / 21) * (0.67 / self.gamma_mc) * xumax_d * (1 - 99 / 238 * xumax_d)
        return k

    def reqd_d(self, fck: float, fy: float, b: float, Mu: float) -> float:
        Mulim_fckbd2 = self.Mulim_const(fy)
        return sqrt(Mu / (Mulim_fckbd2 * fck * b))

    def reqd_xu_d(self, fck: float, b: float, d: float, Mu: float) -> float:
        aa = 1.0
        bb = -238 / 99
        cc = (21 / 17) * (1.5 / 0.67) * (238 / 99) * (Mu / (fck * b * d ** 2))
        xu_d = (-bb - sqrt(bb ** 2 - 4 * aa * cc)) / (2 * aa)
        return xu_d

    def reqd_Ast(self, fck: float, fy: float, b: float, d: float, Mu: float) -> float:
        xu = self.reqd_xu_d(fck, b, d, Mu) * d
        return Mu / ((fy / self.gamma_ms) * (d - (99 / 238 * xu)))

    @staticmethod
    def hor_spacing(b: float, cl_cov: float, bars: List[int]) -> float:
        n = len(bars)
        return (b - (2 * cl_cov) - sum(bars)) / (n - 1)
