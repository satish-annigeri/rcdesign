from math import isclose, pi

from rcdesign.is456.material.rebar import RebarMS, RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection

fe415 = RebarHYSD('Fe 415', 415)
csb = ConcreteStressBlock('IS456 LSM', 0.002, 0.0035)
m20 = Concrete('M20', 20, csb)
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
        pt = 5 * pi * 16**2 / 4 * 100 / (rsec.b * rsec.eff_d())
        # tauc = rsec.conc.tauc(pt)
        assert isclose(rsec.pt(), pt)

    def test_rectbeam05(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        pt = 5 * pi * 16**2 / 4 * 100 / (rsec.b * rsec.eff_d())
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
        C2 = rsec.c_steel.area() * (fsc - fcc)
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
        ast1 = 3 * pi * 16**2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.t_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16**2 / 4
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
        C2 = rsec.c_steel.area() * (fsc - fcc)
        C = C1 + C2
        # Manual calculation for tension force
        D = 450
        D_xu = D - xu
        ast1 = 3 * pi * 16**2 / 4
        x1 = D_xu - 35
        es1 = ecu / xu * x1
        fs1 = rsec.t_steel.rebar.fs(es1)
        ast2 = 2 * pi * 16**2 / 4
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
        Asv = 2 * pi * 8**2 / 4
        fd = 415 / 1.15
        d = rsec.eff_d()
        sv = 150
        Vus = fd * Asv * d / sv

        pt = 5 * pi * 16**2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * 230 * d
        print(Vus)
        assert isclose(rsec.Vu(), Vus+Vuc)

    def test_rectbeam13(self):
        rsec = RectBeamSection(230, 450, m20, t_st, c_st, sh_st, 25)
        d = rsec.eff_d()
        # Modify stirrup details
        nlegs = 4
        bar_dia = 10
        sv = 125
        # Manual calculation for shear reinforcement
        Asv = nlegs * pi * bar_dia**2 / 4
        fd = 415 / 1.15
        Vus = fd * Asv * d / sv
        # Manual calculation for concrete
        pt = 5 * pi * 16**2 / 4 * 100 / (230 * d)
        tauc = rsec.conc.tauc(pt)
        Vuc = tauc * 230 * d
        V = Vus + Vuc
        print(Vus, Vuc, V)
        assert isclose(rsec.Vu(nlegs, bar_dia, sv), V)
