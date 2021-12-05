from math import isclose, pi, sin, cos
from scipy.optimize import brentq

from rcdesign.is456.material.rebar import (
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    BentupBars,
    ShearRebarGroup,
    LateralTies,
)
from rcdesign.is456.material.concrete import (
    ConcreteLSMCompression,
    ConcreteLSMFlexure,
    Concrete,
)
from rcdesign.is456.section import (
    RectBeamSection,
    FlangedBeamSection,
    RectColumnSection,
)
from rcdesign.utils import floor, rootsearch


fe415 = RebarHYSD("Fe 415", 415)
csb = ConcreteLSMFlexure("IS456 LSM")
m20 = Concrete("M20", 20, csb)
c1 = RebarLayer([16, 16], 35)
t1 = RebarLayer([16, 16, 16], -35)
t2 = RebarLayer([16, 16], -70)

long_st = RebarGroup(fe415, [c1, t1, t2])
v_st = Stirrups(fe415, 2, 8, 150)
sh_st = ShearRebarGroup([v_st])
rsec = RectBeamSection(230, 450, m20, long_st, sh_st, 25)


class TestRectBeamSection:
    def test_rectbeam01(self):
        xumax = 0.0035 / (0.0055 + long_st.rebar.fd / long_st.rebar.Es)
        assert rsec.xumax() == xumax

    def test_rectbeam02(self):
        d = rsec.D - rsec.long_steel.dc
        xumax = 0.0035 / (0.0055 + long_st.rebar.fd / long_st.rebar.Es) * d
        mulim = 17 / 21 * rsec.conc.fd * rsec.b * xumax * (d - (99 / 238 * xumax))
        assert rsec.mulim(d) == mulim

    def test_rectbeam03(self):
        dc = (3 * 35 + 2 * 70) / (3 + 2)
        d = rsec.D - dc
        assert rsec.eff_d(120) == d

    def test_rectbeam04(self):
        xu = 100
        rsec_pt = rsec.pt(xu)
        d = rsec.eff_d(xu)
        ast = 5 * pi * 16 ** 2 / 4
        pt = ast * 100 / (rsec.b * d)
        # tauc = rsec.conc.tauc(pt)
        assert isclose(rsec_pt, pt)

    def test_rectbeam05(self):
        xu = 100
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (rsec.b * rsec.eff_d(xu))
        tauc = rsec.conc.tauc(pt)
        assert isclose(rsec.tauc(xu), tauc)

    def test_rectbeam06(self):
        xu = 190
        ecu = 0.0035
        dc = 35
        C, _ = rsec.C(xu, ecu)
        # Manual calculation
        C1 = 17 / 21 * rsec.conc.fd * rsec.b * xu
        fd = rsec.conc.fd
        x = xu - dc
        esc = ecu / xu * x
        fsc = rsec.long_steel.rebar.fs(esc)
        fcc = rsec.conc.fc(x / xu, fd)
        C2 = c1.area * (fsc - fcc)
        assert isclose(C, C1 + C2)

    def test_rectbeam07(self):
        xu = 190
        ecu = 0.0035
        C = rsec.conc.area(0, 1, rsec.conc.fd) * xu * rsec.b
        # Manual calculation
        C1 = 17 / 21 * xu * rsec.conc.fd * rsec.b
        C2 = 0.0
        assert isclose(C, C1 + C2)

    def test_rectbeam08(self):
        xu = 190
        ecu = 0.0035

        T, M = rsec.T(xu, ecu)
        # Manual calculation for tension force
        D = 450
        D_xu = D - xu
        ast1 = 3 * pi * 16 ** 2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.long_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16 ** 2 / 4
        x2 = D_xu - 70
        es2 = ecu / xu * x2
        fs2 = rsec.long_steel.rebar.fs(es2)
        T_manual = ast1 * fs1 + ast2 * fs2
        M_manual = ast1 * fs1 * x1 + ast2 * fs2 * x2
        assert isclose(T, T_manual) and isclose(M, M_manual)

    def test_rectbeam09(self):
        xu = 190
        ecu = 0.0035
        # Methods to calculate C and T
        C_T = rsec.C_T(xu, ecu)
        # Manual calculation for compression force
        C1 = 17 / 21 * rsec.conc.fd * rsec.b * xu
        fd = rsec.conc.fd
        x = xu - 35
        esc = ecu / xu * x
        fsc = rsec.long_steel.rebar.fs(esc)
        fcc = rsec.conc.fc(x / xu, fd)
        C2 = 2 * pi * 16 ** 2 / 4 * (fsc - fcc)
        C = C1 + C2
        # Manual calculation for tension force
        D = 450
        D_xu = D - xu
        ast1 = 3 * pi * 16 ** 2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.long_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16 ** 2 / 4
        x2 = D_xu - 70
        es2 = ecu / xu * x2
        fs2 = rsec.long_steel.rebar.fs(es2)
        T = ast1 * fs1 + ast2 * fs2

        assert isclose(C_T, C - T)

    def test_rectbeam10(self):
        xu = rsec.xu(0.0035)
        assert isclose(xu, 136.21019, rel_tol=1e-3)

    def test_rectbeam11(self):
        xu, Mu = rsec.analyse(0.0035)
        assert isclose(xu, 136.21019, rel_tol=1e-3) and isclose(Mu, 127872548.021942)

    def test_rectbeam12(self):
        fe415 = RebarHYSD("Fe 415", 415)
        csb = ConcreteLSMFlexure("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        c1 = RebarLayer([16, 16], 35)
        t1 = RebarLayer([16, 16, 16], -35)
        t2 = RebarLayer([16, 16], -70)

        long_st = RebarGroup(fe415, [c1, t1, t2])
        v_st = Stirrups(fe415, 2, 8, 150)
        sh_st = ShearRebarGroup([v_st])
        rsec = RectBeamSection(230, 450, m20, long_st, sh_st, 25)

        Asv = 2 * pi * 8 ** 2 / 4
        fd = 415 / 1.15
        xu = 100
        b = 230
        d = rsec.eff_d(xu)
        sv = 150
        Vus = fd * Asv * d / sv
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (b * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * b * d
        # print("===", d, tauc, Vuc, Vus, rsec.Vu(xu))
        vuc, vus = rsec.Vu(xu)

        assert isclose(vuc + sum(vus), Vuc + Vus)

    def test_rectbeam13(self):
        fe415 = RebarHYSD("Fe 415", 415)
        csb = ConcreteLSMFlexure("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        c1 = RebarLayer([16, 16], 35)
        t1 = RebarLayer([16, 16, 16], -35)
        t2 = RebarLayer([16, 16], -70)

        long_st = RebarGroup(fe415, [c1, t1, t2])
        nlegs = 2
        bar_dia = 8
        sv = 150
        alpha_deg = 45
        v_st = Stirrups(fe415, nlegs, bar_dia, sv, alpha_deg)
        sh_st = ShearRebarGroup([v_st])
        b = 230
        D = 450
        rsec = RectBeamSection(b, D, m20, long_st, sh_st, 25)

        xu = 100
        d = rsec.eff_d(xu)
        alpha = alpha_deg * pi / 180
        # Manual calculation for shear reinforcement
        Asv = nlegs * pi * bar_dia ** 2 / 4 * (sin(alpha) + cos(alpha))
        fd = 415 / 1.15
        Vus = fd * Asv * d / sv
        # Manual calculation for concrete
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * b * d
        print("***", pt, tauc, d, Vuc)
        V = Vus + Vuc
        vuc, vus = rsec.Vu(xu)
        assert isclose(vuc + sum(vus), V)

    def test_rectbeam13a(self):
        fe415 = RebarHYSD("Fe 415", 415)
        csb = ConcreteLSMFlexure("IS456 LSM")
        m20 = Concrete("M20", 20, csb)
        c1 = RebarLayer([16, 16], 35)
        t1 = RebarLayer([16, 16, 16], -35)

        long_st = RebarGroup(fe415, [c1, t1])
        sv = 150
        v_st = Stirrups(fe415, 2, 8, sv)
        alpha_deg = 45
        bup = BentupBars(fe415, [16, 16], alpha_deg, 0)
        sh_st = ShearRebarGroup([v_st, bup])
        b = 230
        D = 450
        rsec = RectBeamSection(b, D, m20, long_st, sh_st, 25)

        xu = 100
        d = rsec.eff_d(xu)
        # Manual calculation for shear reinforcement - Vertical stirrups
        Asv1 = pi / 4 * (2 * 8 ** 2)
        fd = 415 / 1.15
        Vus1 = fd * Asv1 * d / sv
        # Manual calculation for shear reinforcement - Bent-up bars
        alpha = alpha_deg * pi / 180
        Asv2 = pi / 4 * (2 * 16 ** 2)
        Vus2 = fd * Asv2 * sin(alpha)
        # Manual calculation for concrete
        pt = pi / 4 * (3 * 16 ** 2) * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * b * d
        V = Vuc + Vus1 + Vus2
        # Method
        vuc, vus = rsec.Vu(xu)
        print("***", type(vus), vus, Vuc, Vus1, Vus2)
        assert isclose(vuc + sum(vus), V)

    def test_rectbeam14(self):
        xu = 100
        d = rsec.eff_d(xu)
        fd = 415 / 1.15
        mof = 25

        # Modify stirrup details
        # Vu = 125e3
        # nlegs = 2
        # bar_dia = 8

        # # Manual calculation for shear capacity of shear reinforcement
        # Asv = nlegs * pi * bar_dia ** 2 / 4

        # # Manual calculation for shear capacity of concrete
        # pt = 5 * pi * 16 ** 2 / 4 * 100 / (230 * d)
        # tauc = rsec.conc.tauc(pt)
        # Vuc = tauc * 230 * d
        # Vus = Vu - Vuc
        # sv = floor(fd * Asv * d / Vus, mof)
        # assert isclose(rsec.sv(xu, Vu, nlegs, bar_dia, mof), sv)

    def test_rectbeam15(self):
        assert rsec.long_steel.dc_max(450) == (43, 372)

    def test_rectbeam16(self):
        ecu = 0.0035
        x1, x2 = rootsearch(rsec.C_T, 10, rsec.D, 10, ecu)
        x = brentq(rsec.C_T, x1, x2, args=(ecu,))
        assert rsec.xu(0.0035) == x

    # adjust_x for layer exactly at the neutral axis
    def test_rectbeam17(self):
        D = 450
        xu = 100
        l1 = RebarLayer([16, 16, 16], xu)
        long_st = RebarGroup(fe415, [l1])
        rsec = RectBeamSection(230, 450, m20, long_st, sh_st, 25)
        rsec.adjust_x(xu)
        assert rsec.long_steel.layers[0].stress_type == "neutral"

    def test_rectbeam18(self):
        D = 450
        xu = 100
        assert rsec.has_compr_steel(xu)


def para_area(x1, x2, xu):
    k = 0.002 / 0.0035
    z1 = max((x1 / xu) / k, 0)
    z2 = min((x2 / xu) / k, 1)
    a = ((z2 ** 2 - z1 ** 2) - (z2 ** 3 - z1 ** 3) / 3) * k
    return a


def rect_area(x1, x2, xu):
    k = 0.002 / 0.0035
    z1 = max(x1 / xu, k)
    z2 = max(x2 / xu, 1)
    a = z2 - z1
    return a


def para_moment(x1, x2, xu):
    k = 0.002 / 0.0035
    z1 = max((x1 / xu) / k, 0)
    z2 = min((x2 / xu) / k, 1)
    m = ((z2 ** 3 - z1 ** 3) * 2 / 3 - (z2 ** 4 - z1 ** 4) / 4) * k ** 2
    return m


def rect_moment(x1, x2, xu):
    k = 0.002 / 0.0035
    z1 = max(x1 / xu, k)
    z2 = max(x2 / xu, 1)
    m = (z2 ** 2 - z1 ** 2) / 2
    return m


bw = 230
bf = 1000
Df = 150
long_st = RebarGroup(fe415, [t1, t2])
tsec = FlangedBeamSection(230, 450, bf, Df, m20, long_st, sh_st, 25)


class TestFlangedBeamSection:
    def test_flangedbeam01(self):
        assert tsec.bw == 230

    def test_flangedbeam02(self):
        tsec.bw = 250
        assert tsec.bw == 250

    # Without compression steel
    def test_flangedbeam03(self):
        xu = 160  # xu > Df
        fd = tsec.conc.fd
        # Calculate compression force manually
        C_web_conc = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        x1 = xu - tsec.Df
        x2 = xu
        a1 = para_area(x1, x2, xu)
        a1 *= fd * xu * (tsec.bf - tsec.bw)
        a2 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        C = C_web_conc + a1 + a2
        CC, _ = tsec.C(xu, 0.0035)
        assert CC == C

    def test_flangedbeam04(self):
        xu = 150  # xu = Df
        fd = tsec.conc.fd
        # Calculate compression force in concrete manually
        # Web
        C_web_conc = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        x1 = xu - tsec.Df
        x2 = xu
        # Flange
        a1 = para_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        a2 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        C = C_web_conc + a1 + a2
        # Method
        CC, _ = tsec.C(xu, 0.0035)
        assert CC == C

    def test_flangedbeam05(self):
        xu = 120  # xu > Df
        fd = tsec.conc.fd
        # Calculate compression force in concrete manually
        # Web
        C_web_conc = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        x1 = xu - tsec.Df
        x2 = xu
        # Flange
        a1 = para_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        a2 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        C = C_web_conc + a1 + a2
        # Method
        CC, _ = tsec.C(xu, 0.0035)
        assert CC == C

    # Compression force, with compression steel
    long_st = RebarGroup(fe415, [c1, t1, t2])

    def test_flangedbeam06(self):
        xu = 160  # xu > Df
        fd = tsec.conc.fd
        # Compression force in compression steel
        x = xu - 35
        esc = 0.0035 / xu * x
        fsc = tsec.long_steel.rebar.fs(esc)
        fcc = tsec.conc.fc(x / xu, tsec.conc.fd)
        C_steel = tsec.long_steel.area_comp(xu) * (fsc - fcc)
        # Calculate compression force in concrete manually
        # Web
        C_web_conc = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        x1 = xu - tsec.Df
        x2 = xu
        # Flange
        a1 = para_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        a2 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        C = C_steel + C_web_conc + a1 + a2
        # Method
        CC, _ = tsec.C(xu, 0.0035)
        assert CC == C

    # Tension force. Method inherited from RectBeamSection
    def test_flangedbeam07(self):
        ecu = 0.0035
        xu = 160  # xu > Df
        # Manual calculation of tension force
        D = 450
        D_xu = D - xu
        es1 = ecu / xu * (D_xu - 35)
        fs1 = tsec.long_steel.rebar.fs(es1)
        ast1 = 3 * pi * 16 ** 2 / 4
        es2 = ecu / xu * (D_xu - 70)
        fs2 = tsec.long_steel.rebar.fs(es2)
        ast2 = 2 * pi * 16 ** 2 / 4
        T_manual = ast1 * fs1 + ast2 * fs2
        T, _ = tsec.T(xu, ecu)
        assert T == T_manual

    # Moment capacity based on compression force
    def test_flangedbeam08(self):
        D = 450
        xu = 160  # xu > Df, assumed
        d = tsec.eff_d(xu)
        fd = tsec.conc.fd
        # Compression force in compression steel
        dc = 35
        x = xu - dc
        esc = 0.0035 / xu * x
        fsc = tsec.long_steel.rebar.fs(esc)
        fcc = tsec.conc.fc(x / xu, tsec.conc.fd)
        a0 = tsec.long_steel.area_comp(xu) * (fsc - fcc)
        m0 = a0 * (xu - dc)
        # Calculate compression force in concrete manually
        # Web
        a1 = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        m1 = para_moment(0, xu, xu) + rect_moment(0, xu, xu)
        m1 *= xu ** 2 * tsec.conc.fd * tsec.bw
        # Flange
        x1 = xu - tsec.Df
        x2 = xu

        a2 = para_area(x1, x2, xu) * xu * fd * (tsec.bf - tsec.bw)
        m2 = para_moment(x1, x2, xu) * xu ** 2 * fd * (tsec.bf - tsec.bw)
        a3 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        m3 = rect_moment(x1, x2, xu) * xu ** 2 * fd * (tsec.bf - tsec.bw)
        C = a0 + a1 + a2 + a3
        M = m0 + m1 + m2 + m3
        Mu_manual = M + C * (d - xu)
        # Method
        Mu = tsec.Mu(xu, 0.0035)
        assert Mu == Mu_manual

    # Moment capacity based on compression force
    def test_flangedbeam09(self):
        long_st = RebarGroup(fe415, [c1, t1, t2])
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, long_st, sh_st, 25)
        ecu = 0.0035
        D = 450
        xu = 160  # xu > Df, assumed
        d = tsec.eff_d(xu)
        fd = tsec.conc.fd
        xu, Mu = tsec.analyse(0.0035)
        # Manual calculation
        C1, _ = tsec.C(xu, ecu)
        T2, _ = tsec.T(xu, ecu)
        assert isclose(C1, T2)


class TestRectColumn:
    def test_rectcol_01(self):
        m20 = Concrete("M20", 20, ConcreteLSMCompression)
        long_st = RebarGroup(
            RebarHYSD("Fe 415", 415),
            [RebarLayer([20, 20, 20], 50), RebarLayer([20, 20, 20], 50)],
        )
        lat_ties = LateralTies(RebarHYSD("Fe 415", 415), 8)
        col = RectColumnSection(230, 600, m20, long_st, lat_ties, 40)
        assert col.Asc == 6 * pi * 20 ** 2 / 4
        assert col.k(1200) == 2

    def test_rectcol_02(self):
        m20 = Concrete("M20", 20, ConcreteLSMCompression)
        long_st = RebarGroup(
            RebarHYSD("Fe 415", 415),
            [RebarLayer([20, 20, 20], 50), RebarLayer([20, 20, 20], 50)],
        )
        lat_ties = LateralTies(RebarHYSD("Fe 415", 415), 8)
        col = RectColumnSection(230, 600, m20, long_st, lat_ties, 40)
        assert col.C(500) == 0.0
        # assert col.C(900) == 230 * 0.945820105820106
