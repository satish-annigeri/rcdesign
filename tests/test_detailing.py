import pytest
from numpy import pi
from fractions import Fraction
from rcdesign.is456.detailing import Beam, Slab, Column, Exposure


class TestBeam:
    def test_01(self):
        b = 230
        D = 450
        d = D - 25 - 8
        fy = 500
        beam = Beam()
        assert beam.Asc_max(b, D) == 0.04 * b * D
        assert beam.Ast_max(b, D) == 0.04 * b * D
        assert beam.Ast_min(b, d, fy) == 0.85 / fy * b * d
        df = 150
        dw = D - df
        assert beam.Ast_side_face(b, dw) == 0
        assert beam.Ast_side_face(b, 750) == 0.1 / 100 * b * 750
        assert beam.min_hor_spacing(16, 20) == 25
        assert beam.min_ver_spacing(16, 20) == 16
        assert beam.min_ver_spacing(12, 20) == 15
        assert beam.min_ver_spacing(20, 20) == 20
        assert beam.nominal_cover_durability(Exposure.MILD, 16, 20) == 20
        assert beam.nominal_cover_durability(Exposure.MODERATE, 16, 20) == 30
        assert beam.nominal_cover_durability(Exposure.SEVERE, 16, 20) == 45
        assert beam.nominal_cover_durability(Exposure.SEVERE, 16, 35) == 40
        assert beam.nominal_cover_durability(Exposure.VERY_SEVERE, 16, 20) == 50
        assert beam.nominal_cover_durability(Exposure.VERY_SEVERE, 16, 35) == 45
        assert beam.nominal_cover_durability(Exposure.EXTREME, 16, 20) == 75
        with pytest.raises(NotImplementedError):
            assert beam.nominal_cover_fire()
        assert beam.sv_max(d, 90) == min(300, 0.75 * d)
        assert beam.sv_max(300, 90) == min(300, 0.75 * 300)
        assert beam.sv_max(d, 45) == min(300, d)
        assert beam.sv_max(275, 45) == min(300, 275)
        Asv = 2 * pi / 4 * 8**2
        fds = Fraction(100, 115)
        assert beam.sv_min(b, fy, Asv) == Asv * fds * min(415, fy) / (0.4 * b)

    def test_02(self):
        beam = Beam()
        with pytest.raises(AttributeError):
            assert beam.nominal_cover_durability(Exposure.SEVEREX, 16, 20)


class TestSlab:
    def test_01(self):
        slab = Slab()
        assert slab.bardia_max(150) == 150 / 8.0
        assert slab.nominal_cover_durability(Exposure.MILD, 16, 20) == 20
        assert slab.Ast_min(150, 250) == 0.15 / 100 * 1000 * 150
        assert slab.Ast_min(150, 415) == 0.12 / 100 * 1000 * 150
        assert slab.Ast_max(150) == 0.04 * 1000 * 150
        assert slab.max_hor_spacing(130, True) == 3 * 130
        assert slab.max_hor_spacing(130, False) == 5 * 130
        with pytest.raises(NotImplementedError):
            assert slab.nominal_cover_fire()


class TestColumn:
    def test_01(self):
        b = 230
        D = 450
        col = Column()
        assert col.Asc_max(b, D) == 6 / 100 * b * D
        assert col.Asc_min(b, D) == 0.8 / 100 * b * D
        assert col.bardia_min() == 12
        assert col.lateral_ties_dia(20) == max(20 / 4, 6)
        assert col.lateral_ties_dia(25) == max(25 / 4, 6)
        assert col.lateral_ties_pitch(b, 12) == 16 * 12
        assert col.lateral_ties_pitch(b, 16) == b
        assert col.lateral_ties_pitch(b, 20) == b
        assert col.lateral_ties_pitch(300, 20) == 300
