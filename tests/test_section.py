from math import isclose, pi, sin

from rcdesign.is456.material.rebar import RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection
from rcdesign.utils import floor


fe415 = RebarHYSD("Fe 415", 415)
csb = ConcreteStressBlock("IS456 LSM", 0.002, 0.0035)
m20 = Concrete("M20", 20, csb)
t1 = RebarLayer(35, [16, 16, 16])
t2 = RebarLayer(70, [16, 16])
t_st = RebarGroup(fe415, [t1, t2])
c1 = RebarLayer(35, [16, 16])
c_st = RebarGroup(fe415, [c1])
sh_st = Stirrups(fe415, 2, 8, 150)


class TestRectBeamSection:
    def test_rectbeam01(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xumax = 0.0035 / (0.0055 + t_st.rebar.fd / t_st.rebar.Es)
        assert rsec.xumax() == xumax

    def test_rectbeam02(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        d = rsec.D - rsec.t_steel._dc()
        xumax = 0.0035 / (0.0055 + t_st.rebar.fd / t_st.rebar.Es) * d
        mulim = 17 / 21 * rsec.conc.fd * rsec.b * xumax * (d - (99 / 238 * xumax))
        assert rsec.mulim(d) == mulim

    def test_rectbeam03(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        dc = (3 * 35 + 2 * 70) / (3 + 2)
        d = rsec.D - dc
        assert rsec.eff_d() == d

    def test_rectbeam04(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (rsec.b * rsec.eff_d())
        # tauc = rsec.conc.tauc(pt)
        assert isclose(rsec.pt(), pt)

    def test_rectbeam05(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (rsec.b * rsec.eff_d())
        tauc = rsec.conc.tauc(pt)
        assert isclose(rsec.tauc(), tauc)

    def test_rectbeam06(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xu = 190
        ecu = 0.0035
        dc = 35
        C, _ = rsec.C(xu, ecu)
        # Manual calculation
        C1 = 17 / 21 * rsec.conc.fd * rsec.b * xu
        fd = rsec.conc.fd
        x = xu - dc
        esc = ecu / xu * x
        fsc = rsec.c_steel.rebar.fs(esc)
        fcc = rsec.conc.fc(x / xu, fd)
        C2 = rsec.c_steel.area * (fsc - fcc)
        assert isclose(C, C1 + C2)

    def test_rectbeam07(self):
        rsec = RectBeamSection(230, 450, m20, t_st, None, sh_st, 25)
        xu = 190
        ecu = 0.0035
        C, _ = rsec.C(xu, ecu)
        # Manual calculation
        C1 = 17 / 21 * rsec.conc.fd * rsec.b * xu
        C2 = 0.0
        assert isclose(C, C1 + C2)

    def test_rectbeam08(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xu = 190
        ecu = 0.0035

        T, M = rsec.T(xu, ecu)
        # Manual calculation for tension force
        D = 450
        D_xu = D - xu
        ast1 = 3 * pi * 16 ** 2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.t_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16 ** 2 / 4
        x2 = D_xu - 70
        es2 = ecu / xu * x2
        fs2 = rsec.t_steel.rebar.fs(es2)
        T_manual = ast1 * fs1 + ast2 * fs2
        M_manual = ast1 * fs1 * x1 + ast2 * fs2 * x2
        assert isclose(T, T_manual) and isclose(M, M_manual)

    def test_rectbeam09(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xu = 190
        ecu = 0.0035
        # Methods to calculate C and T
        C_T = rsec.C_T(xu, ecu)
        # Manual calculation for compression force
        C1 = 17 / 21 * rsec.conc.fd * rsec.b * xu
        fd = rsec.conc.fd
        x = xu - 35
        esc = ecu / xu * x
        fsc = rsec.c_steel.rebar.fs(esc)
        fcc = rsec.conc.fc(x / xu, fd)
        C2 = rsec.c_steel.area * (fsc - fcc)
        C = C1 + C2
        # Manual calculation for tension force
        D = 450
        D_xu = D - xu
        ast1 = 3 * pi * 16 ** 2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.t_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16 ** 2 / 4
        x2 = D_xu - 70
        es2 = ecu / xu * x2
        fs2 = rsec.t_steel.rebar.fs(es2)
        T = ast1 * fs1 + ast2 * fs2

        assert isclose(C_T, C - T)

    def test_rectbeam10(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xu = rsec.xu(0.0035)
        assert isclose(xu, 136.21019, rel_tol=1e-3)

    def test_rectbeam11(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        xu, Mu = rsec.analyse(0.0035)
        assert isclose(xu, 136.21019, rel_tol=1e-3) and isclose(Mu, 127872548.021942)

    def test_rectbeam12(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        Asv = 2 * pi * 8 ** 2 / 4
        fd = 415 / 1.15
        d = rsec.eff_d()
        sv = 150
        Vus = fd * Asv * d / sv

        pt = 5 * pi * 16 ** 2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * 230 * d
        print(Vus)
        assert isclose(rsec.Vu(), Vus + Vuc)

    def test_rectbeam13(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        d = rsec.eff_d()
        # Modify stirrup details
        nlegs = 4
        bar_dia = 10
        sv = 125
        alpha = rsec.shear_steel._alpha_deg * pi / 180
        # Manual calculation for shear reinforcement
        Asv = nlegs * pi * bar_dia ** 2 / 4 * sin(alpha)
        fd = 415 / 1.15
        Vus = fd * Asv * d / sv
        # Manual calculation for concrete
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * 230 * d
        V = Vus + Vuc
        assert isclose(rsec.Vu(nlegs, bar_dia, sv), V)

    def test_rectbeam14(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        d = rsec.eff_d()
        fd = 415 / 1.15
        mof = 25

        # Modify stirrup details
        Vu = 125e3
        nlegs = 2
        bar_dia = 8

        # Manual calculation for shear capacity of shear reinforcement
        Asv = nlegs * pi * bar_dia ** 2 / 4

        # Manual calculation for shear capacity of concrete
        pt = 5 * pi * 16 ** 2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * 230 * d
        Vus = Vu - Vuc
        sv = floor(fd * Asv * d / Vus, mof)
        assert isclose(rsec.sv(Vu, nlegs, bar_dia, mof), sv)

    def test_rectbeam15(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        assert rsec.t_steel.dc_max() == 70


bw = 230
bf = 1000
Df = 150


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


class TestFlangedBeamSection:
    def test_flangedbeam01(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, None, sh_st, 25)
        assert tsec.bw == 230

    def test_flangedbeam02(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, None, sh_st, 25)
        tsec.bw = 250
        assert tsec.bw == 250

    # Without compression steel
    def test_flangedbeam03(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, None, sh_st, 25)
        xu = 160  # xu > Df
        fd = tsec.conc.fd
        # Calculate compression force manually
        C_web_conc = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        x1 = xu - tsec.Df
        x2 = xu
        a1 = para_area(x1, x2, xu)
        print("***", a1)
        a1 *= fd * xu * (tsec.bf - tsec.bw)
        a2 = rect_area(x1, x2, xu) * fd * xu * (tsec.bf - tsec.bw)
        C = C_web_conc + a1 + a2
        CC, _ = tsec.C(xu, 0.0035)
        print(C_web_conc, a1, a2, C, CC)
        assert CC == C

    def test_flangedbeam04(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, None, sh_st, 25)
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
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, None, sh_st, 25)
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
    def test_flangedbeam06(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, c_st, sh_st, 25)
        xu = 160  # xu > Df
        fd = tsec.conc.fd
        # Compression force in compression steel
        x = xu - 35
        esc = 0.0035 / xu * x
        fsc = tsec.c_steel.rebar.fs(esc)
        fcc = tsec.conc.fc(x / xu, tsec.conc.fd)
        print(esc, fsc, fcc)
        C_steel = tsec.c_steel.area * (fsc - fcc)
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
        print(C_steel, C_web_conc, a1, a2, C, CC)
        assert CC == C

    # Tension force. Method inherited from RectBeamSection
    def test_flangedbeam07(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, c_st, sh_st, 25)
        ecu = 0.0035
        xu = 160  # xu > Df
        # Manual calculation of tension force
        D = 450
        D_xu = D - xu
        es1 = ecu / xu * (D_xu - 35)
        fs1 = tsec.t_steel.rebar.fs(es1)
        ast1 = 3 * pi * 16 ** 2 / 4
        es2 = ecu / xu * (D_xu - 70)
        fs2 = tsec.t_steel.rebar.fs(es2)
        ast2 = 2 * pi * 16 ** 2 / 4
        T_manual = ast1 * fs1 + ast2 * fs2
        T, _ = tsec.T(xu, ecu)
        assert T == T_manual

    # Moment capacity based on compression force
    def test_flangedbeam08(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, c_st, sh_st, 25)
        D = 450
        d = tsec.eff_d()
        xu = 160  # xu > Df, assumed
        fd = tsec.conc.fd
        # Compression force in compression steel
        dc = 35
        x = xu - dc
        esc = 0.0035 / xu * x
        fsc = tsec.c_steel.rebar.fs(esc)
        fcc = tsec.conc.fc(x / xu, tsec.conc.fd)
        print(esc, fsc, fcc)
        a0 = tsec.c_steel.area * (fsc - fcc)
        m0 = a0 * (xu - dc)
        # Calculate compression force in concrete manually
        # Web
        a1 = 17 / 21 * tsec.conc.fd * tsec.bw * xu
        m1 = para_moment(0, xu, xu) + rect_moment(0, xu, xu)
        # print(a1, m1, m1 * xu**2 * tsec.conc.fd * tsec.bw)
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
        Mu = tsec.Mu(d, xu, 0.0035)
        assert Mu == Mu_manual

    # Moment capacity based on compression force
    def test_flangedbeam09(self):
        tsec = FlangedBeamSection(230, 450, bf, Df, m20, t_st, c_st, sh_st, 25)
        ecu = 0.0035
        D = 450
        d = tsec.eff_d()
        xu = 160  # xu > Df, assumed
        fd = tsec.conc.fd
        xu, Mu = tsec.analyse(0.0035)
        # Manual calculation
        C1, M1 = tsec.C(xu, ecu)
        T2, M2 = tsec.T(xu, ecu)
        assert isclose(C1, T2)
