from dataclasses import dataclass
from enum import Enum
from rcdesign.is456.constants import fds


class Exposure(Enum):
    MILD = 1
    MODERATE = 2
    SEVERE = 3
    VERY_SEVERE = 4
    EXTREME = 5


@dataclass
class Beam:
    def min_ver_spacing(
        self, max_bardia: float, nominal_agg_size: float = 20.0
    ) -> float:
        return max(15.0, 2 / 3 * nominal_agg_size, max_bardia)

    def min_hor_spacing(
        self, max_bardia: float, nominal_agg_size: float = 20.0
    ) -> float:
        return max(max_bardia, nominal_agg_size + 5.0)

    def Ast_min(self, b: float, d: float, fy: float) -> float:
        return 0.85 / fy * b * d

    def Ast_max(self, b: float, D: float) -> float:
        return 0.04 * b * D

    def Asc_max(self, b: float, D: float) -> float:
        return 0.04 * b * D

    def Ast_side_face(self, bw: float, dw: float) -> float:
        if dw < 750:
            return 0.0
        else:
            return 0.1 / 100 * bw * dw

    def sv_max(self, d: float, alpha: float = 90.0) -> float:
        return min(300.0, 0.75 * d if alpha == 90 else d)

    def sv_min(self, b: float, fy: float, Asv: float) -> float:
        return Asv * fds * min(415, fy) / (0.4 * b)

    def nominal_cover_durability(self, exposure: Exposure, bardia: float, fck: float) -> float:
        match exposure:
            case Exposure.MILD:
                cover = 20 if bardia > 12 else 15
            case Exposure.MODERATE:
                cover = 30
            case Exposure.SEVERE:
                cover = 45 if fck < 35 else 40
            case Exposure.VERY_SEVERE:
                cover = 50 if fck < 35 else 45
            case Exposure.EXTREME:
                cover = 75
            case _:
                raise AttributeError
        return float(cover)

    def nominal_cover_fire(self) -> float:
        raise NotImplementedError


@dataclass
class Slab:
    def Ast_min(self, D: float, fy: float) -> float:
        pst = 0.15 if fy < 415 else 0.12
        return pst / 100 * 1000 * D

    def Ast_max(self, D: float) -> float:
        return Beam().Ast_max(1000.0, D)

    def bardia_max(self, D: float) -> float:
        return D / 8.0

    def max_hor_spacing(self, d: float, main_bars: bool = True) -> float:
        if main_bars:
            return max(3 * d, 300.0)
        else:
            return max(5 * d, 450.0)

    def nominal_cover_durability(self, exposure: Exposure, bardia: float, fck: float) -> float:
        return Beam().nominal_cover_durability(exposure, bardia, fck)

    def nominal_cover_fire(self) -> float:
        raise NotImplementedError


@dataclass
class Column:
    def Asc_min(self, b: float, D: float) -> float:
        return 0.8 / 100 * b * D

    def Asc_max(self, b: float, D: float) -> float:
        return 6 / 100.0 * b * D

    def bardia_min(self) -> float:
        return 12.0

    def lateral_ties_pitch(self, b: float, bardia_min: float) -> float:
        return min(b, 16 * bardia_min, 300.0)

    def lateral_ties_dia(self, bardia_max: float) -> float:
        return max(bardia_max / 4.0, 6.0)
