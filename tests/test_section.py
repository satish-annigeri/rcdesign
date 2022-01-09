from math import isclose, pi, sin, cos, sqrt
from scipy.optimize import brentq

from rcdesign.is456 import ecy, ecu
from rcdesign.is456.rebar import (
    Rebar,
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    BentupBars,
    ShearRebarGroup,
    LateralTie,
    StressType,
)
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.section import (
    FlangedBeamSection,
    RectBeamSection,
    RectColumnSection,
    # FlangedBeamSection,
    # RectColumnSection,
)
from rcdesign.utils import floor, rootsearch


def calc_fsc(ecy, ecmax, xu, x, a, rebar, conc):
    esc = ecmax / xu * x
    fsc = rebar.fs(esc)
    fcc = (2 * (esc / ecy) - (esc / ecy) ** 2) * conc.fd if esc < 0.002 else conc.fd
    Fsc = a * (fsc - fcc)
    Msc = Fsc * x
    return Fsc, Msc


def calc_fst(ecmax, xu, x, a, rebar):
    est = ecmax / xu * x
    fst = rebar.fs(est)
    Fst = fst * a
    Mst = Fst * x
    return Fst, Mst


class TestRectBeamSection:
    def test_01(self):
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [20, 20, 20], -35)
        b = 230
        D = 450
        main_st = RebarGroup([L1, L2])
        shear_st = Stirrups(fe415, 2, 8, 150)
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        rsec.calc_xc()
        assert rsec.long_steel.layers[0].xc == 35
        assert rsec.long_steel.layers[1].xc == D - 35
        xu = 75
        rsec.calc_stress_type(xu)
        assert (
            rsec.long_steel.layers[0].stress_type(xu) == StressType.STRESS_COMPRESSION
        )
        assert rsec.long_steel.layers[1].stress_type(xu) == StressType.STRESS_TENSION

    def test_02(self):
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16], -70)
        L3 = RebarLayer(fe415, [20, 20, 20], -35)
        b = 230
        D = 450
        main_st = RebarGroup([L1, L2, L3])
        shear_st = Stirrups(fe415, 2, 8, 150)
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        rsec.calc_xc()
        assert rsec.long_steel.layers[0].xc == 35
        assert rsec.long_steel.layers[1].xc == D - 70
        assert rsec.long_steel.layers[2].xc == D - 35
        xu = 75
        rsec.calc_stress_type(xu)
        assert (
            rsec.long_steel.layers[0].stress_type(xu) == StressType.STRESS_COMPRESSION
        )
        assert rsec.long_steel.layers[1].stress_type(xu) == StressType.STRESS_TENSION
        # Manual calculation for effective depth
        ast1 = 2 * 16 ** 2 * pi / 4
        ast2 = 3 * 20 ** 2 * pi / 4
        ast = ast1 + ast2
        x1 = D - 70
        x2 = D - 35
        xbar = (ast1 * x1 + ast2 * x2) / (ast)
        assert rsec.eff_d(xu) == xbar
        pt = (ast) / (b * xbar) * 100
        assert rsec.pt(xu) == pt

    def test_03(self):
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [20, 20, 20], -35)
        b = 230
        D = 450
        main_st = RebarGroup([L2])
        shear_st = Stirrups(fe415, 2, 8, 150)
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        rsec.calc_xc()
        xu = 75
        assert not rsec.has_compr_steel(xu)

        main_st = RebarGroup([L1, L2])
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        rsec.calc_xc()
        xu = 75
        assert rsec.has_compr_steel(xu)

    def test_04(self):
        def tauc(pt, fck):
            beta = max(1, 0.8 * fck / (6.89 * pt))
            tc = ((0.85 * sqrt(0.8 * fck)) * (sqrt(1 + 5 * beta) - 1)) / (6 * beta)
            return tc

        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        m30 = Concrete("M30", 30)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [20, 20, 20], -35)
        b = 230
        D = 450
        main_st = RebarGroup([L1, L2])
        shear_st = Stirrups(fe415, 2, 8, 150)
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        rsec.calc_xc()
        ast = 3 * pi / 4 * 20 ** 2
        d = D - 35
        pt = (ast) / (b * d) * 100
        xu = 75
        assert rsec.tauc(xu) == tauc(pt, 20)
        rsec = RectBeamSection(b, D, csb, m30, main_st, shear_st, 25)
        assert rsec.tauc(xu) == tauc(pt, 30)

    def test_05(self):
        # Doubly reinforced section
        b = 230
        D = 450
        fe415 = RebarHYSD("Fe 415", 415)
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16], -70)
        L3 = RebarLayer(fe415, [16, 16, 16], -35)
        main_st = RebarGroup([L1, L2, L3])
        vstirrups = Stirrups(fe415, 2, 8, 150)
        shear_st = ShearRebarGroup([vstirrups])
        rsec = RectBeamSection(b, D, csb, m20, main_st, shear_st, 25)
        xu = 75
        ecmax = ecu
        Fc, Mc, Ft, Mt = rsec.F_M(xu, ecmax)
        fcc = (17 / 21) * m20.fd * b * xu
        mcc = 139 / 294 * m20.fd * b * xu ** 2
        xc = xu - rsec.long_steel.layers[0].xc
        a = pi / 4 * 2 * 16 ** 2
        fsc, msc = calc_fsc(ecy, ecmax, xu, xc, a, fe415, m20)
        xt1 = rsec.long_steel.layers[1].xc - xu
        xt2 = rsec.long_steel.layers[2].xc - xu
        ast1 = pi / 4 * 2 * 16 ** 2
        ast2 = pi / 4 * 3 * 16 ** 2
        fst1, mst1 = calc_fst(ecmax, xu, xt1, ast1, fe415)
        fst2, mst2 = calc_fst(ecmax, xu, xt2, ast2, fe415)
        ft = fst1 + fst2
        mt = mst1 + mst2
        # assert isclose(Fc, fcc + fsc)
        assert Mc == mcc + msc
        assert Ft == ft
        assert Mt == mt
        Fc, Mc = rsec.C(xu, ecmax)
        assert Fc == (17 / 21) * m20.fd * b * xu + fsc
        Ft, Mt = rsec.T(xu, ecmax)
        assert Ft == ft
        assert Mt == mt
        C_T = rsec.C_T(xu, ecmax)
        assert C_T == Fc - Ft

        # Equilibrium NA location
        calc_xu = rsec.xu(ecmax)
        assert isclose(calc_xu, 136.2101931)

        Mu = rsec.Mu(calc_xu, ecmax)
        fcc = (17 / 21) * m20.fd * b * calc_xu
        mcc = 139 / 294 * m20.fd * b * calc_xu ** 2
        xc = calc_xu - rsec.long_steel.layers[0].xc
        a = pi / 4 * 2 * 16 ** 2
        fsc, msc = calc_fsc(ecy, ecmax, calc_xu, xc, a, fe415, m20)
        xt1 = rsec.long_steel.layers[1].xc - calc_xu
        xt2 = rsec.long_steel.layers[2].xc - calc_xu
        ast1 = pi / 4 * 2 * 16 ** 2
        ast2 = pi / 4 * 3 * 16 ** 2
        fst1, mst1 = calc_fst(ecmax, calc_xu, xt1, ast1, fe415)
        fst2, mst2 = calc_fst(ecmax, calc_xu, xt2, ast2, fe415)
        ft = fst1 + fst2
        mt = mst1 + mst2
        mu = mcc + msc + mst1 + mst2
        assert isclose(Mu, mu)

        xu, mu = rsec.analyse(ecmax)
        assert isclose(calc_xu, 136.2101931)
        assert Mu == mu

        Vuc, Vus = rsec.Vu(xu)
        d = (ast1 * xt1 + ast2 * xt2) / (ast1 + ast2) + calc_xu
        pt = (ast1 + ast2) * 100 / (b * d)
        tauc = m20.tauc(pt)
        vuc = tauc * b * d
        vus = fe415.fd * 2 * pi / 4 * 8 ** 2 * d / 150
        assert Vuc + sum(Vus) == vuc + vus


class TestFlangedBeamSection:
    def test_01(self):
        b = 230
        D = 450
        bf = 1000
        df = 150
        fe415 = RebarHYSD("Fe 415", 415)
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        L1 = RebarLayer(fe415, [20, 20, 20], -35)
        main_st = RebarGroup([L1])
        stirrup = Stirrups(fe415, 2, 8, 150)
        shear_st = ShearRebarGroup([stirrup])
        tsec = FlangedBeamSection(b, D, bf, df, csb, m20, main_st, shear_st, 25)
        assert tsec.bw == 230
        tsec.bw = 250
        assert tsec.bw == 250
        tsec.bw = 230
        ecmax = ecu
        xu = 75  # xu < df
        ccw = 17 / 21 * m20.fd * b * xu
        mcw = 139 / 294 * m20.fd * b * xu ** 2
        Ccw, Mcw = tsec.Cw(xu, ecmax)
        assert isclose(Ccw, ccw)
        assert isclose(Mcw, mcw)
        ccf = 17 / 21 * m20.fd * (bf - b) * xu
        mcf = 139 / 294 * m20.fd * (bf - b) * xu ** 2
        Ccf, Mcf = tsec.Cf(xu, ecmax)
        assert isclose(Ccf, ccf)
        assert isclose(Mcf, mcf)
        C, Mc = tsec.C_M(xu, ecmax)
        assert isclose(C, ccw + ccf)
        assert isclose(Mc, mcw + mcf)
        T, Mt = tsec.T(xu, ecmax)
        x = tsec.long_steel.layers[0].xc - xu
        a = pi / 4 * (3 * 20 ** 2)
        Fst, Mst = calc_fst(ecmax, xu, x, a, fe415)
        assert T == Fst
        assert Mt == Mst
        C_T = tsec.C_T(xu, ecmax)
        assert isclose(C_T, ccw + ccf - Fst)

    def test_02(self):
        # xu < Df, singly reinforced
        b = 300
        D = 475
        bf = 800
        df = 150
        fe415 = RebarHYSD("Fe 415", 415)
        csb = LSMStressBlock("LSM Flexure")
        m25 = Concrete("M25", 25)
        L1 = RebarLayer(fe415, [18, 18], -70)
        L2 = RebarLayer(fe415, [20, 20, 20], -35)
        main_st = RebarGroup([L1, L2])
        stirrup = Stirrups(fe415, 2, 8, 150)
        shear_st = ShearRebarGroup([stirrup])
        tsec = FlangedBeamSection(b, D, bf, df, csb, m25, main_st, shear_st, 25)
        ecmax = ecu
        xu = 72.43  # xu < df
        ccw = 17 / 21 * m25.fd * b * xu
        mcw = 139 / 294 * m25.fd * b * xu ** 2
        Ccw, Mcw = tsec.Cw(xu, ecmax)
        assert isclose(Ccw, ccw)
        assert isclose(Mcw, mcw)
        ccf = 17 / 21 * m25.fd * (bf - b) * xu
        mcf = 139 / 294 * m25.fd * (bf - b) * xu ** 2
        Ccf, Mcf = tsec.Cf(xu, ecmax)
        assert isclose(Ccf, ccf)
        assert isclose(Mcf, mcf)
        C, Mc = tsec.C_M(xu, ecmax)
        assert isclose(C, ccw + ccf)
        assert isclose(Mc, mcw + mcf)
        T, Mt = tsec.T(xu, ecmax)
        x1 = tsec.long_steel.layers[0].xc - xu
        x2 = tsec.long_steel.layers[1].xc - xu
        a1 = pi / 4 * (2 * 18 ** 2)
        a2 = pi / 4 * (3 * 20 ** 2)
        Fst1, Mst1 = calc_fst(ecmax, xu, x1, a1, fe415)
        Fst2, Mst2 = calc_fst(ecmax, xu, x2, a2, fe415)
        assert T == Fst1 + Fst2
        assert Mt == Mst1 + Mst2
        C_T = tsec.C_T(xu, ecmax)
        assert isclose(C_T, ccw + ccf - (Fst1 + Fst2))
        calc_xu = tsec.xu(ecmax)
        assert isclose(calc_xu, 72.426740174037)
        Mu = tsec.Mu(calc_xu, ecmax)
        assert isclose(Mu, 208251760.06)
        calc_xu, Mu = tsec.analyse(ecmax)
        assert isclose(calc_xu, 72.426740174037) and isclose(Mu, 208251760.06)

    def test_03(self):
        # xu > Df, singly reinforced
        b = 300
        D = 475
        bf = 800
        df = 150
        fe415 = RebarHYSD("Fe 415", 415)
        csb = LSMStressBlock("LSM Flexure")
        m25 = Concrete("M25", 25)
        L1 = RebarLayer(fe415, [18, 18], -70)
        L2 = RebarLayer(fe415, [20, 20, 20], -35)
        main_st = RebarGroup([L1, L2])
        stirrup = Stirrups(fe415, 2, 8, 150)
        shear_st = ShearRebarGroup([stirrup])
        tsec = FlangedBeamSection(b, D, bf, df, csb, m25, main_st, shear_st, 25)
        ecmax = ecu
        xu = 160  # xu > df
        Ccw, Mcw = tsec.Cw(xu, ecmax)
        Ccf, Mcf = tsec.Cf(xu, ecmax)
        assert isclose(Ccw, 433904.7619) and isclose(Mcw, 40546394.56)
        assert isclose(Ccf, 717290.475) and (Mcf, 67538282.28)
        T, M = tsec.T(xu, ecmax)
        assert isclose(T, 523771.7908) and isclose(M, 140227993.1)

    def test_04(self):
        # xu > Df, doubly reinforced
        b = 300
        D = 475
        bf = 800
        df = 150
        fe415 = RebarHYSD("Fe 415", 415)
        csb = LSMStressBlock("LSM Flexure")
        m25 = Concrete("M25", 25)
        L1 = RebarLayer(fe415, [18, 18], 35)
        L2 = RebarLayer(fe415, [18, 18], -70)
        L3 = RebarLayer(fe415, [20, 20, 20], -35)
        main_st = RebarGroup([L1, L2, L3])
        stirrup = Stirrups(fe415, 2, 8, 150)
        shear_st = ShearRebarGroup([stirrup])
        tsec = FlangedBeamSection(b, D, bf, df, csb, m25, main_st, shear_st, 25)
        ecmax = ecu
        xu = 160  # xu > df
        Ccw, Mcw = tsec.Cw(xu, ecmax)
        Ccf, Mcf = tsec.Cf(xu, ecmax)
        assert isclose(Ccw, 433904.7619) and isclose(Mcw, 40546394.56)
        assert isclose(Ccf, 717290.475) and (Mcf, 67538282.28)
        T, M = tsec.T(xu, ecmax)
        assert isclose(T, 523771.7908) and isclose(M, 140227993.1)
        C, M = tsec.C_M(xu, ecmax)
        assert isclose(C, 1324250.023) and isclose(M, 129716525.08)


class TestRectColumnSection:
    def calc_Fsc(
        self, D: float, asc: float, xu: float, xc: float, conc: Concrete, rebar: Rebar
    ) -> float:
        z = (xu - xc) / D
        k = xu / D
        if k > 1:
            esc_ecy = z / (k - 3 / 7)
        else:
            esc_ecy = z / (4 / 7 * k)
        esc = esc_ecy * ecy
        fsc = rebar.fs(esc)
        if esc_ecy <= 0:
            fcc = 0.0
        elif esc_ecy >= 1:
            fcc = conc.fd
        else:
            fcc = (2 * esc_ecy - esc_ecy ** 2) * conc.fd
        return asc * (fsc - fcc)

    def calc_c(self, z1: float, z2: float, k: float) -> float:
        if (z1 < k - 1) or (z1 > k) or (z2 < k - 1) or z2 > k:
            return 0.0
        if z1 > z2:
            z1, z2 = z2, z1
        zcy = k - 3 / 7
        if z2 <= zcy:
            a1 = (z2 ** 2 - z1 ** 2) / zcy - (z2 ** 3 - z1 ** 3) / zcy ** 2 / 3
            a2 = 0.0
        elif z1 >= zcy:
            a1 = 0.0
            a2 = z2 - z1
        else:
            a1 = (zcy ** 2 - z1 ** 2) / zcy - (zcy ** 3 - z1 ** 3) / zcy ** 2 / 3
            a2 = z2 - zcy
        return a1 + a2

    def calc_m(self, z1: float, z2: float, k: float) -> float:
        if (z1 < k - 1) or (z1 > k) or (z2 < k - 1) or z2 > k:
            return 0.0
        if z1 > z2:
            z1, z2 = z2, z1
        zcy = k - (3 / 7)
        if z2 <= zcy:
            m1 = (2 / 3 * (z2 ** 3 - z1 ** 3) / zcy) - (
                (z2 ** 4 - z1 ** 4) / zcy ** 2 / 4
            )
            m2 = 0.0
        elif z1 >= zcy:
            m1 = 0.0
            m2 = (z2 ** 2 - zcy ** 2) / 2
        else:
            m1 = (2 / 3 / zcy * (zcy ** 3 - z1 ** 3)) - (
                (zcy ** 4 - z1 ** 4) / zcy ** 2 / 4
            )
            m2 = (z2 ** 2 - zcy ** 2) / 2
        return m1 + m2

    def calc_cf(self, z1: float, z2: float, k: float) -> float:
        if (z1 < 0) or (z1 > k) or (z2 < 0) or z2 > k:
            return 0.0
        if z1 > z2:
            z1, z2 = z2, z1
        zcy = 4 / 7 * k
        if z2 <= zcy:
            a1 = (z2 ** 2 - z1 ** 2) / zcy - (z2 ** 3 - z1 ** 3) / zcy ** 2 / 3
            a2 = 0.0
        elif z1 >= zcy:
            a1 = 0.0
            a2 = z2 - z1
        else:
            a1 = (zcy ** 2 - z1 ** 2) / zcy - (zcy ** 3 - z1 ** 3) / zcy ** 2 / 3
            a2 = z2 - zcy
        return a1 + a2

    def calc_mf(self, z1: float, z2: float, k: float) -> float:
        if (z1 < 0) or (z1 > k) or (z2 < 0) or z2 > k:
            return 0.0
        if z1 > z2:
            z1, z2 = z2, z1
        zcy = 4 / 7 * k
        if z2 <= zcy:
            m1 = (2 / 3 * (z2 ** 3 - z1 ** 3) / zcy) - (
                (z2 ** 4 - z1 ** 4) / zcy ** 2 / 4
            )
            m2 = 0.0
        elif z1 >= zcy:
            m1 = 0.0
            m2 = (z2 ** 2 - zcy ** 2) / 2
        else:
            m1 = (2 / 3 / zcy * (zcy ** 3 - z1 ** 3)) - (
                (zcy ** 4 - z1 ** 4) / zcy ** 2 / 4
            )
            m2 = (z2 ** 2 - zcy ** 2) / 2
        return m1 + m2

    def test_01(self):
        b = 230
        D = 500
        csb = LSMStressBlock("LSM Compression")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16, 16], 50)
        L2 = RebarLayer(fe415, [16, 16], D / 2)
        L3 = RebarLayer(fe415, [16, 16, 16], -50)
        long_st = RebarGroup([L1, L2, L3])
        lat_ties = LateralTie(fe415, 8, 150)
        colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
        assert colsec.Asc == pi / 4 * (8 * 16 ** 2)
        assert colsec.k(1000) == 2

    def test_02(self):
        b = 230
        D = 450
        csb = LSMStressBlock("LSM Compression")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16, 16], 50)
        L2 = RebarLayer(fe415, [16, 16], D / 2)
        L3 = RebarLayer(fe415, [16, 16, 16], -50)
        long_st = RebarGroup([L1, L2, L3])
        lat_ties = LateralTie(fe415, 8, 150)
        colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
        xu = 675
        k = xu / D  # k = 1.5
        C, M = colsec.C_M(xu)
        cc = self.calc_c(k - 1, k, k) * m20.fd * b * D
        mm = self.calc_m(k - 1, k, k) * m20.fd * b * D ** 2
        fsc1 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, 50, m20, fe415)
        fsc2 = self.calc_Fsc(D, 2 * pi / 4 * 16 ** 2, xu, D / 2, m20, fe415)
        fsc3 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, D - 50, m20, fe415)
        c = cc + fsc1 + fsc2 + fsc3
        m = mm + fsc1 * abs(xu - 50) + fsc2 * abs(xu - 225) + fsc3 * abs(xu - 400)
        assert isclose(C, c)
        assert isclose(M, m)

    def test_03(self):
        b = 230
        D = 450
        csb = LSMStressBlock("LSM Compression")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16, 16], 50)
        L2 = RebarLayer(fe415, [16, 16], D / 2)
        L3 = RebarLayer(fe415, [16, 16, 16], -50)
        long_st = RebarGroup([L1, L2, L3])
        lat_ties = LateralTie(fe415, 8, 150)
        colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
        xu = 300
        k = xu / D  # k = 2 / 3
        C, M = colsec.C_M(xu)
        cc = self.calc_cf(0, k, k) * m20.fd * b * D
        mm = self.calc_mf(0, k, k) * m20.fd * b * D ** 2
        fsc1 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, 50, m20, fe415)
        fsc2 = self.calc_Fsc(D, 2 * pi / 4 * 16 ** 2, xu, D / 2, m20, fe415)
        fsc3 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, D - 50, m20, fe415)
        c = cc + fsc1 + fsc2 + fsc3
        m = mm + fsc1 * abs(xu - 50) + fsc2 * abs(xu - 225) + fsc3 * abs(xu - 400)
        assert isclose(C, c)
        assert isclose(M, m)
        assert colsec.C_M(0)[0] == 0.0  # Test for k = 0

    def test_04(self):
        b = 230
        D = 450
        csb = LSMStressBlock("LSM Compression")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16, 16], 50)
        L2 = RebarLayer(fe415, [16, 16], D / 2)
        L3 = RebarLayer(fe415, [16, 16, 16], -50)
        long_st = RebarGroup([L1, L2, L3])
        lat_ties = LateralTie(fe415, 8, 150)
        colsec = RectColumnSection(b, D, csb, m20, long_st, lat_ties, 35)
        k = 2.0
        xu = k * D
        cc = self.calc_c(k - 1, k, k) * m20.fd * b * D
        mm = self.calc_m(k - 1, k, k) * m20.fd * b * D ** 2
        fsc1 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, 50, m20, fe415)
        fsc2 = self.calc_Fsc(D, 2 * pi / 4 * 16 ** 2, xu, D / 2, m20, fe415)
        fsc3 = self.calc_Fsc(D, 3 * pi / 4 * 16 ** 2, xu, D - 50, m20, fe415)
        C, M = colsec.C_M(xu)
        c = cc + fsc1 + fsc2 + fsc3
        m = mm + fsc1 * abs(xu - 50) + fsc2 * abs(xu - 225) + fsc3 * abs(xu - 400)
        assert isclose(C, c)
        assert isclose(M, m)
