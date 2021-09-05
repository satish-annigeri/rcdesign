from math import isclose, pi, sin

from rcdesign.is456.material.rebar import RebarMS, RebarHYSD, RebarLayer, RebarGroup, Stirrups
from rcdesign.is456.material.concrete import ConcreteStressBlock, Concrete

class TestShearRebar:
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
        st = Stirrups(fe415, 2, 8, 40)
        assert st.sv(80e3, 400) == None

    def test_shearrebar05(self):
        fe415 = RebarHYSD('Fe 415', 415)
        st = Stirrups(fe415, 2, 8)
        Vus = 80e3
        d = 400
        sv = fe415.fd * (2 * pi * 8**2 / 4) * d * sin(pi/2) / Vus
        assert st.sv(Vus, d) == sv

