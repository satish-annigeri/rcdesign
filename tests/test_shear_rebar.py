from math import isclose, pi, sin

from rcdesign.is456.material.rebar import BentupBars, RebarMS, RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete

class TestStirrup:
    def test_shearrebar01(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8)
        assert st.Asv == 2 * pi * 8**2 / 4

    def test_shearrebar02(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8)
        assert (st.nlegs == 2) and (st.bar_dia == 8)

    def test_shearrebar03(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8)
        st.nlegs = 4
        st.bar_dia = 10
        assert (st.nlegs == 4) and (st.bar_dia == 10) and (st.Asv == 4 * pi * 10**2 / 4)

    def test_shearrebar04(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8, 150, 40)
        assert st.calc_sv(80e3, 400) == None

    def test_shearrebar05(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8)
        Vus = 80e3
        d = 400
        sv = fe415.fd * (2 * pi * 8**2 / 4) * d * sin(pi/2) / Vus
        assert st.calc_sv(Vus, d) == sv

    def test_shearrebar06(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8, 150, 45)
        Vus = 80e3
        d = 400
        sv = st.rebar.fd * (2 * pi * 8**2 / 4) * d * sin(pi/2) * sin(45 * pi / 180) / Vus
        assert st.calc_sv(Vus, d) == sv

class TestBentupBars:
    def test_bentupbars01(self):
        fe415 = RebarHYSD('Fe 415', 415)
        bup = BentupBars(fe415, [16, 16], 150)
        assert (bup.Asv == 2 * pi * 16**2 / 4) and (bup._sv == 150)

    def test_bentupbars02(self):
        fe415 = RebarHYSD('Fe 415', 415)
        bup = BentupBars(fe415, [16, 16], 150, 45)
        Vus = 80e3
        d = 400
        sv = bup.rebar.fd * (2 * pi * 16**2 / 4) * d * sin(45 * pi / 180) / Vus
        assert bup.calc_sv(Vus, d) == sv

