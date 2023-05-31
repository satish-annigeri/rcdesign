from fractions import Fraction
import numpy as np
import numpy.typing as ntp


gamma_c: Fraction = Fraction(3, 2)  # 1.5
gamma_s: Fraction = Fraction(115, 100)  # 1.15
ecy: float = 0.002
ecu: float = 0.0035
Es: float = 2e5
fdc: Fraction = Fraction(2, 3) / gamma_c
fds: Fraction = 1 / gamma_s
_A1: Fraction = Fraction(2, 3) * Fraction(4, 7)
_A2: Fraction = Fraction(3, 7)
_A = _A1 + _A2
k1: Fraction = _A * fdc
k2: Fraction = 1 - (_A1 * (Fraction(5, 8) * Fraction(4, 7)) + _A2 * (Fraction(4, 7) + Fraction(1, 2) * Fraction(3, 7))) / _A

inel_strain: ntp.NDArray = np.array(
    [[0.8, 0.0], [0.85, 0.0001], [0.9, 0.0003], [0.95, 0.0007], [0.975, 0.001], [1, 0.002]]
)
