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
sh_st = Stirrups(fe415, 2, 8)


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

