from math import pi, sqrt, isclose, ceil

from rcdesign.is456.design import Beam

xumax_d = lambda fy: 0.0035 / (fy / (1.15 * 2e5) + 0.0055)

mulim_const = (
    lambda fy: (17 * 0.67) / (21 * 1.5) * xumax_d(fy) * (1 - 99 / 238 * xumax_d(fy))
)

d_req = lambda fck, fy, b, Mu: sqrt(Mu / (fck * b * mulim_const(fy)))


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
        beam = Beam()

        assert isclose(beam.xumax_d(250), xumax_d(250))
        assert isclose(beam.xumax_d(415), xumax_d(415))
        assert isclose(beam.xumax_d(500), xumax_d(500))

    def test_02(self):
        beam = Beam()
        assert isclose(beam.Mulim_const(250), mulim_const(250))
        assert isclose(beam.Mulim_const(415), mulim_const(415))
        assert isclose(beam.Mulim_const(500), mulim_const(500))

    def test_03(self):
        fck = 20
        fy = 415
        b = 230
        d = 450 - 25 - 16 / 2
        Mu = 100e6
        beam = Beam()
        assert isclose(beam.reqd_d(fck, fy, b, Mu), d_req(fck, fy, b, Mu))

    def test_04(self):
        fck = 20
        b = 230
        d = 450 - 25 - 16 / 2
        Mu = 100e6
        beam = Beam()
        assert isclose(beam.reqd_xu_d(fck, b, d, Mu), reqd_xu_d(fck, b, d, Mu))

    def test_05(self):
        beam = Beam()
        assert beam.bar_area(20) == pi / 4 * 20 ** 2
        dia = 16
        ast = 625.2
        n = int(ceil(ast / (pi / 4 * dia ** 2)))
        assert beam.num_bars(ast, dia) == n

    def test_06(self):
        beam = Beam()
        fck = 20
        fy = 415
        b = 230
        d = 450 - 25 - 16 / 2
        Mu = 100e6
        Ast = beam.reqd_Ast(fck, fy, b, d, Mu)
        assert Ast == reqd_ast(fck, fy, b, d, Mu)
        n = beam.num_bars(Ast, 16)
        assert n == int(ceil(Ast / (pi / 4 * 16 ** 2)))
        assert beam.spacing(b, 25, [16] * n) == (b - 2 * 25 - n * 16) / (n - 1)
