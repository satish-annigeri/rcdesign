from math import isclose, pi

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
