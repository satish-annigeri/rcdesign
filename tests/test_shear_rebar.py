from math import pi, sin, cos

from rcdesign.is456.material.rebar import (
    RebarHYSD,
    ShearRebarGroup,
    Stirrups,
    BentupBars,
)


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


class TestShearReinfGroup:
    def test_sheargroup01(self):
        fe415 = RebarHYSD("fe 415", 415)
        d = 415.0
        vst = Stirrups(fe415, 2, 8, 150)
        asv1 = 2 * pi / 4 * 8 ** 2
        vus1 = fe415.fd * asv1 * d / vst._sv
        ist = Stirrups(fe415, 2, 8, 150, 45)
        asv3 = asv1
        vus3 = 0
        bup = BentupBars(fe415, [16, 16], 45)
        asv2 = pi / 4 * (2 * 16 ** 2)
        vus2 = fe415.fd * asv2 * sin(bup._alpha_deg * pi / 180)
        shear_gr = ShearRebarGroup([vst, bup])
        assert shear_gr.Asv() == [asv1, asv2]
        assert shear_gr.Vus(d) == [vus1, vus2]
        assert shear_gr.get_type() == {
            "vertical_stirrups": 1,
            "inclined_stirrups": 0,
            "single_bentup_bars": 1,
            "series_bentup_bars": 0,
        }
