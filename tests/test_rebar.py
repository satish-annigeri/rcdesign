from math import isclose, sqrt, pi, sin, cos
import pytest


from rcdesign.is456.stressblock import LSMStressBlock, LSMStressBlock
from rcdesign.is456 import ecy, ecu
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    RebarMS,
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    StressType,
    ShearRebarType,
    Stirrups,
    BentupBars,
    LateralTie,
    ShearRebarGroup,
)


class TestRebarMS:
    def test_01(self):
        ms = RebarMS("MS", 250)
        assert ms.fs(0) == 0
        esy = ms.fy / ms.gamma_m / ms.Es
        assert ms.fs(esy) == ms.fd
        assert ms.fs(esy + 0.001) == ms.fd
        assert ms.fs(0.001) == 0.001 * ms.Es


class TestRebarHYSD:
    def test_01(self):
        fe415 = RebarHYSD("Fe 415", 250)
        assert fe415.fs(0) == 0
        esy = fe415.fd / fe415.Es + 0.002
        assert fe415.fs(esy) == fe415.fd
        fs1 = 0.8 * fe415.fd
        es1 = fs1 / fe415.Es
        assert fe415.fs(0.5 * es1) == 0.5 * fe415.Es * es1
        fs2 = 0.85 * fe415.fd
        es2 = fs2 / fe415.Es + 0.0001
        assert fe415.fs(es2) == fs2
        es = (es1 + es2) / 2
        assert fe415.fs(es) == (fs1 + fs2) / 2


class TestRebarLayer:
    def test_01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [20, 16, 20], 35)
        assert L1.max_dia == 20
        assert L1.area == pi * (2 * 20 ** 2 + 16 ** 2) / 4
        assert L1.dc == 35
        assert L1.xc == 35
        L1.xc = 450
        assert L1.xc == 35
        L1.dc = -35
        assert L1.dc == -35
        L1.xc = 450
        assert L1.xc == 450 - 35
        assert L1.dc == -35

    def test_02(self):
        D = 450
        xu = 75
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        assert L1.stress_type(xu) == StressType.STRESS_COMPRESSION
        assert L1.x(xu) == 40
        L1.dc = xu
        assert L1.stress_type(75) == StressType.STRESS_NEUTRAL
        L1.dc = -35
        L1.xc = D
        assert L1.stress_type(xu) == StressType.STRESS_TENSION
        assert L1.x(75) == xu - (D - 35)

    def test_03(self):
        D = 450
        xu = 75
        ecmax = ecu
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        assert L1.es(xu, ecmax) == ecmax / xu * L1.x(xu)

    def test_04(self):
        xu = 75
        ecmax = ecu
        dc = 35
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], dc)
        ec = ecmax / xu * (xu - dc)
        assert L1.fs(xu, ecmax) == fe415.fs(ec)

    def test_05(self):
        ecmax = ecu
        xu = 75
        dc = 35
        x = xu - dc
        ec = ecmax / xu * x
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], dc)
        asc = pi * (2 * 16 ** 2) / 4
        z = x / xu
        fsc = fe415.fs(ec)
        fcc = m20.fd * csb._fc_(ec)
        C = asc * (fsc - fcc)
        d = {"x": x, "esc": ec, "f_sc": fsc, "f_cc": fcc, "C": C, "M": C * x}
        f, m, res = L1.force_compression(xu, csb, m20, ecmax)
        assert isclose(f, C)
        assert isclose(m, C * x)
        assert res == d

    def test_06(self):
        ecmax = ecu
        D = 450
        xu = 75
        dc = -35
        x = D + dc - xu
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16, 16], dc)
        L1.xc = D
        ast = pi * (3 * 16 ** 2) / 4
        est = ecmax / xu * x
        fst = fe415.fs(est)
        T = ast * fst
        d = {"x": x, "est": est, "f_st": fst, "T": T, "M": T * x}
        assert L1.force_tension(xu, ecmax) == (T, T * x, d)

    def test_07(self):
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        assert L1.bar_list() == "2-16"
        L2 = RebarLayer(fe415, [20, 16, 20], -35)
        assert L2.bar_list() == "1-16;2-20"

    def test_08(self):
        D = 450
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [20, 20], -70)
        L2.xc = D
        L3 = RebarLayer(fe415, [20, 16, 20], -35)
        L3.xc = D
        assert L1 < L2 < L3
        assert L3 > L2 > L1
        assert L1 != L2
        assert L1 <= L2 <= L3
        assert L3 >= L2 >= L1
        assert L1 == L1


class TestRebarGroup:
    def test_01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16, 16], -35)
        main_st = RebarGroup([L1, L2])
        D = 450
        xu = 75

        assert main_st.area == pi / 4 * (5 * 16 ** 2)
        assert main_st.layers[0].xc == 35
        assert main_st.layers[1].xc == -35
        main_st.calc_xc(D)
        assert main_st.layers[0].xc == 35
        assert main_st.layers[1].xc == D - 35
        assert main_st.has_comp_steel(xu)
        assert not main_st.has_comp_steel(25)
        assert main_st.area_comp(xu) == pi / 4 * (2 * 16 ** 2)
        assert main_st.area_tension(xu) == pi / 4 * (3 * 16 ** 2)

    def test_02(self):
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16, 16], -35)
        main_st = RebarGroup([L1, L2])
        D = 450
        xu = 75
        main_st.calc_xc(D)
        main_st.calc_stress_type(xu)
        assert main_st.layers[0]._stress_type == StressType.STRESS_COMPRESSION
        assert main_st.layers[1]._stress_type == StressType.STRESS_TENSION

    def test_03(self):
        ecmax = ecu
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16], -70)
        L3 = RebarLayer(fe415, [16, 16, 16], -35)
        main_st = RebarGroup([L1, L2, L3])
        D = 450
        xu = 75
        main_st.calc_xc(D)
        main_st.calc_stress_type(xu)
        # Manual calculation -- tension force
        x2 = D - 70 - xu
        x3 = D - 35 - xu
        es2 = ecmax / xu * x2
        es3 = ecmax / xu * x3
        fs2 = fe415.fs(es2)
        fs3 = fe415.fs(es3)
        a2 = 2 * pi / 4 * 16 ** 2
        a3 = 3 * pi / 4 * 16 ** 2
        T = a2 * fs2 + a3 * fs3
        Mt = a2 * fs2 * x2 + a3 * fs3 * x3
        t, mt = main_st.force_tension(xu, ecmax)
        assert t == T
        assert mt == Mt
        # Manual calculatio  - compression force
        x1 = xu - 35
        ec1 = ecmax / xu * x1
        fsc = fe415.fs(ec1)
        ec1d = ec1 / ecy
        fcc = m20.fd * (2 * ec1d - ec1d ** 2)
        a1 = 2 * pi / 4 * 16 ** 2
        C = a1 * (fsc - fcc)
        Mc = C * x1
        c, mc = main_st.force_compression(xu, csb, m20, ecmax)
        assert c == C
        assert mc == Mc
        f1, m1, f2, m2 = main_st.force_moment(xu, csb, m20, ecmax)
        assert (f1 == C) and (f2 == T) and (m1 == Mc) and (m2 == Mt)

    def test_04(self):
        ecmax = ecu
        csb = LSMStressBlock("LSM Flexure")
        m20 = Concrete("M20", 20)
        fe415 = RebarHYSD("Fe 415", 415)
        L1 = RebarLayer(fe415, [16, 16], 35)
        L2 = RebarLayer(fe415, [16, 16], 70)
        L3 = RebarLayer(fe415, [16, 16], -70)
        L4 = RebarLayer(fe415, [16, 16, 16], -35)
        main_st = RebarGroup([L1, L2, L3, L4])
        D = 450
        xu = 75
        main_st.calc_xc(D)
        main_st.calc_stress_type(xu)
        # Manual calculation
        a1 = (2 * pi / 4 * 16 ** 2) + (2 * pi / 4 * 16 ** 2)
        m1 = (2 * pi / 4 * 16 ** 2) * 35 + (2 * pi / 4 * 16 ** 2) * 70
        a2 = (2 * pi / 4 * 16 ** 2) + (3 * pi / 4 * 16 ** 2)
        m2 = (2 * pi / 4 * 16 ** 2) * (D - 70) + (3 * pi / 4 * 16 ** 2) * (D - 35)
        c1, c2 = main_st.centroid(xu)
        assert (c1 == m1 / a1) and (c2 == m2 / a2)


class TestStirrup:
    def test_shearrebar01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8)
        assert st.Asv == 2 * pi * 8 ** 2 / 4

    def test_shearrebar02(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8)
        assert (st.nlegs == 2) and (st.bar_dia == 8)

    def test_shearrebar03(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8)
        st.nlegs = 4
        st.bar_dia = 10
        assert (
            (st.nlegs == 4) and (st.bar_dia == 10) and (st.Asv == 4 * pi * 10 ** 2 / 4)
        )

    def test_shearrebar04(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150, 40)
        assert st.calc_sv(80e3, 400) is None

    def test_shearrebar05(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8)
        Vus = 80e3
        d = 400
        sv = fe415.fd * (2 * pi * 8 ** 2 / 4) * d * sin(pi / 2) / Vus
        assert st.calc_sv(Vus, d) == sv

    def test_shearrebar06(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150, 45)
        Vus = 80e3
        d = 400
        sv = (
            st.rebar.fd
            * (2 * pi * 8 ** 2 / 4)
            * d
            * sin(pi / 2)
            * sin(45 * pi / 180)
            / Vus
        )
        assert st.calc_sv(Vus, d) == sv

    def test_shearrebar07(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150, 45)
        assert st.sv == 150

    def test_shearrebar08(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150, 45)
        d = 415  # Effective depth in mm
        Asv = pi / 4 * 2 * 8 ** 2
        alpha = st._alpha_deg * pi / 180
        Vus = st.rebar.fd * Asv * d / st._sv * (sin(alpha) + cos(alpha))
        assert st.Vus(d) == Vus

    def test_shearrebar09(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150)
        d = 415  # Effective depth in mm
        Asv = pi / 4 * 2 * 8 ** 2
        alpha = st._alpha_deg * pi / 180
        Vus = st.rebar.fd * Asv * d / st._sv
        assert st.Vus(d) == Vus

    def test_shearrebar10(self):
        fe415 = RebarHYSD("Fe 415", 415)
        st = Stirrups(fe415, 2, 8, 150)
        assert st._sv == 150
        st.sv = 125
        assert st._sv == 125


class TestBentupBars:
    def test_bentupbars01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        bup = BentupBars(fe415, [16, 16])
        assert (
            (bup.Asv == 2 * pi * 16 ** 2 / 4)
            and (bup._sv == 0)
            and (bup._alpha_deg == 45)
        )

    def test_bentupbars02(self):
        fe415 = RebarHYSD("Fe 415", 415)
        bup = BentupBars(fe415, [16, 16], 45)
        Vus = bup.rebar.fd * (pi / 4 * (2 * 16 ** 2)) * sin(45 * pi / 180)
        assert bup.Vus() == Vus

    def test_bentupbars03(self):
        fe415 = RebarHYSD("Fe 415", 415)
        d = 415.0
        bup = BentupBars(fe415, [16, 16], 45, 150)
        alpha = 45 * pi / 180
        asv = pi / 4 * (2 * 16 ** 2)
        Vus = bup.rebar.fd * asv * d / bup._sv * (sin(alpha) + cos(alpha))
        assert bup.Vus(d) == Vus


class TestShearRebarGroup:
    def test_sheargroup01(self):
        fe415 = RebarHYSD("fe 415", 415)
        d = 415.0
        vst = Stirrups(fe415, 2, 8, 150)
        asv1 = 2 * pi / 4 * 8 ** 2
        vus1 = fe415.fd * asv1 * d / vst._sv
        ist = Stirrups(fe415, 2, 8, 150, 45)
        alpha = 45 * pi / 180
        asv3 = asv1
        vus3 = fe415.fd * asv1 * d / ist._sv * (sin(alpha) + cos(alpha))
        bup = BentupBars(fe415, [16, 16], 45)
        asv2 = pi / 4 * (2 * 16 ** 2)
        vus2 = fe415.fd * asv2 * sin(bup._alpha_deg * pi / 180)
        bupseries = BentupBars(fe415, [16, 16], 45, 150)
        asv4 = asv2
        vus4 = fe415.fd * asv4 * d / bupseries._sv * (sin(alpha) + cos(alpha))
        shear_gr = ShearRebarGroup([vst, bup, ist, bupseries])
        assert shear_gr.Asv() == [asv1, asv2, asv3, asv4]
        assert shear_gr.Vus(d) == [vus1, vus2, vus3, vus4]
        assert shear_gr.get_type() == {
            ShearRebarType.SHEAR_REBAR_VERTICAL_STIRRUP: 1,
            ShearRebarType.SHEAR_REBAR_INCLINED_STIRRUP: 1,
            ShearRebarType.SHEAR_REBAR_BENTUP_SINGLE: 1,
            ShearRebarType.SHEAR_REBAR_BENTUP_SERIES: 1,
        }


class TestLateralTies:
    def test_01(self):
        fe415 = RebarHYSD("Fe 415", 415)
        lat_tie = LateralTie(fe415, 8, 150)
        assert (lat_tie.bar_dia == 8) and (lat_tie.spacing == 150)
