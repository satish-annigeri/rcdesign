from math import pi, sqrt, isclose, ceil

from rcdesign.is456.design import LSMBeam
from rcdesign.utils import num_bars


def xumax_d(fy: float) -> float:
    return 0.0035 / (fy / (1.15 * 2e5) + 0.0055)


def mulim_const(fy: float) -> float:
    return (17 * 0.67) / (21 * 1.5) * xumax_d(fy) * (1 - 99 / 238 * xumax_d(fy))


def d_req(fck: float, fy: float, b: float, Mu: float) -> float:
    return sqrt(Mu / (fck * b * mulim_const(fy)))


def reqd_xu_d(fck, b, d, Mu):
    aa = 1.0
    bb = -(238 / 99)
    cc = (Mu / (fck * b * d ** 2)) * (21 / 17) * (1.5 / 0.67) * (238 / 99)
    xu_d = (-bb - sqrt(bb ** 2 - 4 * aa * cc)) / (2 * aa)
    return xu_d


def reqd_ast(fck, fy, b, d, Mu):
    xu = reqd_xu_d(fck, b, d, Mu) * d
    ast = Mu / (fy / 1.15 * (d - 99 / 238 * xu))
    return ast


class TestIS456Design:
    def test_01(self):
        beam = LSMBeam()

        assert isclose(beam.xumax_d(250), xumax_d(250))
        assert isclose(beam.xumax_d(415), xumax_d(415))
        assert isclose(beam.xumax_d(500), xumax_d(500))

    def test_02(self):
        beam = LSMBeam()
        assert isclose(beam.Mulim_const(250), mulim_const(250))
        assert isclose(beam.Mulim_const(415), mulim_const(415))
        assert isclose(beam.Mulim_const(500), mulim_const(500))

    def test_03(self):
        fck = 20
        fy = 415
        b = 230
        Mu = 100e6
        beam = LSMBeam()
        assert isclose(beam.reqd_d(fck, fy, b, Mu), d_req(fck, fy, b, Mu))

    def test_04(self):
        fck = 20
        b = 230
        d = 450 - 25 - 16 / 2
        Mu = 100e6
        beam = LSMBeam()
        assert isclose(beam.reqd_xu_d(fck, b, d, Mu), reqd_xu_d(fck, b, d, Mu))

    def test_06(self):
        beam = LSMBeam()
        fck = 20
        fy = 415
        b = 230
        d = 450 - 25 - 16 / 2
        Mu = 100e6
        Ast = beam.reqd_Ast(fck, fy, b, d, Mu)
        assert Ast == reqd_ast(fck, fy, b, d, Mu)
        n = num_bars(Ast, 16)
        assert n == int(ceil(Ast / (pi / 4 * 16 ** 2)))
        assert beam.hor_spacing(b, 25, [16] * n) == (b - 2 * 25 - n * 16) / (n - 1)
