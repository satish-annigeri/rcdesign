from dataclasses import dataclass
from typing import Any, Union
from math import sqrt
from sympy import symbols, nsimplify, integrate
from sympy.core.mul import Mul

import rcdesign.is456 as is456

# from rcdesign.stressblock import StressBlock


@dataclass
class LSMStressBlock:
    label: str = "IS 456 LSM"
    ecy: float = is456.ecy
    ecu: float = is456.ecu

    def __repr__(self):
        s = self.label
        return s

    def isvalid_ecmax(self, ecmax: float) -> float:
        if (ecmax < 0) or (ecmax > self.ecu):
            raise ValueError
        else:
            return ecmax

    def isvalid_k(self, k: float) -> float:
        if k < 0:
            raise ValueError
        else:
            return k

    def isvalid_z(self, z: float, k: float):
        k = self.isvalid_k(k)
        if (z < k - 1) or (z > k):
            raise ValueError
        else:
            return z

    def _ec(self, _k: float, ecmax: float = ecu) -> Union[Mul, Any]:
        ecmax = self.isvalid_ecmax(ecmax)
        z, k = symbols("z k")
        if _k < 0:  # Invalid values for k
            raise ValueError
        elif _k == 0:  # Unstressed condition
            ec = nsimplify(0)
        elif _k <= 1:  # Flexure or axial compression with NA within the section
            ec = (z / nsimplify(self.ecy / ecmax * k)).evalf(subs={"k": _k})
        else:  # Axial compression with NA outside the section
            ec = (z / nsimplify((k - 3 / 7))).evalf(subs={"k": _k})
        return ec

    def ec(self, z: float, k: float, ecmax: float = ecu) -> float:
        _ec = self._ec(k, ecmax)
        return float(_ec.evalf(subs={"z": z}))

    def _fc_(self, ec: float) -> float:
        if (ec < 0) or (ec > self.ecu):
            return 0.0
        ec_ecy = ec / self.ecy
        if ec_ecy < 1:
            return 2 * ec_ecy - ec_ecy**2
        else:
            return 1.0

    def _fc(self, z: float, k: float, ecmax: float = ecu) -> Union[Mul, Any]:
        ecmax = self.isvalid_ecmax(ecmax)
        if k < 0:  # Invalid values for k
            raise ValueError
        elif k == 0:  # Unstressed condition
            fc = nsimplify(0)
        else:  # Flexure or axial compression with NA within the section
            ec = self.ec(z, k, ecmax)
            if ec < 0:
                fc = nsimplify(0)
            elif ec < 1:
                ec_ecy = self._ec(k, ecmax)
                fc = (2 * ec_ecy - ec_ecy**2).evalf(subs={"k": k})
            else:
                fc = nsimplify(1)
        return fc

    def fc(self, z: float, k: float, ecmax: float = ecu) -> float:
        fc = self._fc(z, k, ecmax)
        return float(fc.evalf(subs={"z": z}))

    def C(
        self, z1: float, z2: float, k: float, ecmax: float = ecu
    ) -> Union[float, Any]:
        ecmax = self.isvalid_ecmax(ecmax)
        z = symbols("z")
        k = self.isvalid_k(k)
        if k == 0:
            return 0.0

        z1 = self.isvalid_z(z1, k)
        z2 = self.isvalid_z(z2, k)
        if z1 > z2:
            z1, z2 = z2, z1
        ec1 = self.ec(z1, k)
        ec2 = self.ec(z2, k)
        if ec2 <= 1:  # Parabolic only
            fcp = self._fc(z1, k, ecmax)
            Cp = integrate(fcp, (z, z1, z2))
            Cr = 0.0
        elif ec1 >= 1:  # Rectangular only
            Cp = 0.0
            fcr = self._fc(z1, k, ecmax)
            Cr = integrate(fcr, (z, z1, z2))
        else:  # Both Parabolic and Rectangular
            if k <= 1:  # NA within the section
                zz = self.ecy / ecmax * k
            else:  # NA outside the section
                zz = k - (1 - self.ecy / self.ecu)
            fcp = self._fc(z1, k, ecmax)
            fcr = self._fc(z2, k, ecmax)
            Cp = integrate(fcp, (z, z1, zz))
            Cr = integrate(fcr, (z, zz, z2))
        return Cp + Cr  # type: ignore

    def M(
        self, z1: float, z2: float, k: float, ecmax: float = ecu
    ) -> Union[float, Any]:
        ecmax = self.isvalid_ecmax(ecmax)
        z = symbols("z")
        k = self.isvalid_k(k)
        if k == 0:
            return 0.0

        z1 = self.isvalid_z(z1, k)
        z2 = self.isvalid_z(z2, k)
        if z1 > z2:
            z1, z2 = z2, z1
        ec1 = self.ec(z1, k)
        ec2 = self.ec(z2, k)
        if ec2 <= 1:  # Parabolic only
            fcp = self._fc(z1, k, ecmax)
            Mp = integrate(fcp * z, (z, z1, z2))
            Mr = 0.0
        elif ec1 >= 1:  # Rectangular only
            Mp = 0.0
            fcr = self._fc(z1, k, ecmax)
            Mr = integrate(fcr * z, (z, z1, z2))
        else:  # Both Parabolic and Rectangular
            if k <= 1:  # NA within the section
                zz = self.ecy / ecmax * k
            else:  # NA outside the section
                zz = k - (1 - self.ecy / self.ecu)
            fcp = self._fc(z1, k, ecmax)
            fcr = self._fc(z2, k, ecmax)
            Mp = integrate(fcp * z, (z, z1, zz))
            Mr = integrate(fcr * z, (z, zz, z2))
        return Mp + Mr  # type: ignore


@dataclass
class WSMStressBlock:
    _fcbc: float
    _fst: float

    @property
    def fcbc(self) -> float:
        return self._fcbc

    @fcbc.setter
    def fcbc(self, _fcbc: float) -> None:
        self._fcbc = _fcbc

    @property
    def fst(self) -> float:
        return self._fst

    @fst.setter
    def fst(self, _fst: float) -> None:
        self._fst = _fst

    @property
    def m(self) -> float:
        return 280.0 / (3 * self.fcbc)

    def kb(self, d: float = 1.0) -> float:
        m = self.m
        return (m * self.fcbc) / (m * self.fcbc + self.fst) * d

    def jb(self, d: float = 1.0) -> float:
        return d * (1 - self.kb(d) / 3.0)

    def Qb(self, b: float = 1.0, d: float = 1.0) -> float:
        xb = self.kb(d)
        # print(b, xb, fcbc, d)
        return b * xb * self.fcbc / 2.0 * (d - xb / 3.0)

    def xb(self, d):
        m = self.m
        return m * self.fcbc * d / (self.fst + m * self.fcbc)

    def x(self, b: float, d: float, Ast: float) -> float:
        m = self.m
        ca = b / 2.0
        cb = m * Ast
        cc = -m * Ast * d
        return (-cb + sqrt(cb**2 - 4 * ca * cc)) / (2 * ca)

    def reqd_Asc_Ast(self, b, d, dd: float, M):
        Mb = self.Qb(b, d)
        if M <= Mb:
            x = (1.5 - sqrt(1.5**2 - (6 * M / (self.fcbc * b * d**2)))) * d
            Ast = b * x * self.fcbc / (2 * self.fst)
            Asc = 0.0
            # print('Singly', x, Ast, Asc, M/1e6, Mb/1e6)
        else:
            xb = self.kb(d)
            Ast1 = b * xb * self.fcbc / (2 * self.fst)
            M2 = M - Mb
            Ast2 = M2 / (self.fst * (d - dd))
            Ast = Ast1 + Ast2
            m = self.m
            Asc = (m * Ast2 * (d - xb)) / ((1.5 * m - 1) * (xb - dd))
            # print('Doubly', xb, Asc, Ast, M/1e6, Mb/1e6)
        return Asc, Ast
