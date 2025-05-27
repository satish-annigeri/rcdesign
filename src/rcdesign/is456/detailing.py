from dataclasses import dataclass
from enum import Enum
from rcdesign.is456.constants import fds


class Exposure(Enum):
    """Exposure conditions as per IS 456:2000.
    This enum defines various exposure conditions that affect the design and detailing of concrete structures.

    Attributes:
        MILD: Mild exposure condition.
        MODERATE: Moderate exposure condition.
        SEVERE: Severe exposure condition.
        VERY_SEVERE: Very severe exposure condition.
        EXTREME: Extreme exposure condition.
    """

    MILD = 1
    MODERATE = 2
    SEVERE = 3
    VERY_SEVERE = 4
    EXTREME = 5


@dataclass
class Beam:
    """Class for detailing of beams as per IS 456:2000.
    This class provides methods to calculate various parameters related to beam reinforcement,
    such as minimum and maximum reinforcement areas, bar diameters, spacing, and cover requirements.
    Attributes:
        None
    """

    def min_ver_spacing(self, max_bardia: float, nominal_agg_size: float = 20.0) -> float:
        """Minimum vertical spacing between main reinforcement bars in a beam.
        Args:
            max_bardia (float): Maximum bar diameter in mm.
            nominal_agg_size (float, optional): Nominal size of coarse aggregate in mm. (default=20.0).
        Returns:
            float: Minimum vertical spacing in mm.
        """
        return max(15.0, 2 / 3 * nominal_agg_size, max_bardia)

    def min_hor_spacing(self, max_bardia: float, nominal_agg_size: float = 20.0) -> float:
        """Minimum horizontal spacing between main reinforcement bars in a beam.
        Args:
            max_bardia (float): Maximum bar diameter in mm.
            nominal_agg_size (float, optional): Nominal size of coarse aggregate in mm. (default=20.0).
        Returns:
            float: Minimum horizontal spacing in mm.
        """
        return max(max_bardia, nominal_agg_size + 5.0)

    def Ast_min(self, b: float, d: float, fy: float) -> float:
        """Minimum area of tension reinforcement in a beam.
        Args:
            b (float): Width of the beam in mm.
            d (float): Effective depth of the beam in mm.
            fy (float): Yield strength of the reinforcement in MPa.
        Returns:
            float: Minimum area of tension reinforcement in mm².
        """
        return 0.85 / fy * b * d

    def Ast_max(self, b: float, D: float) -> float:
        """Maximum area of tension reinforcement in a beam.
        Args:
            b (float): Width of the beam in mm.
            D (float): Overall depth of the beam in mm.
        Returns:
            float: Maximum area of tension reinforcement in mm².
        """
        return 0.04 * b * D

    def Asc_max(self, b: float, D: float) -> float:
        """Maximum area of compression reinforcement in a beam.
        Args:
            b (float): Width of the beam in mm.
            D (float): Overall depth of the beam in mm.
        Returns:
            float: Maximum area of compression reinforcement in mm².
        """
        return 0.04 * b * D

    def Ast_side_face(self, bw: float, dw: float) -> float:
        """Area of sideface reinforcement required for beams of large depth.
        Args:
            bw (float): Width of the beam in mm.
            dw (float): Effective depth of the beam in mm.
        Returns:
            float: Area of tension reinforcement required for side face in mm².
        """
        if dw < 750:
            return 0.0
        else:
            return 0.1 / 100 * bw * dw

    def sv_max(self, d: float, alpha: float = 90.0) -> float:
        """Maximum spacing of shear reinforcement in a beam.
        Args:
            d (float): Effective depth of the beam in mm.
            alpha (float, optional): Angle of inclination of the shear reinforcement in degrees. Default is 90.
        Returns:
            float: Maximum spacing of shear reinforcement in mm.
        """
        return min(300.0, 0.75 * d if alpha == 90 else d)

    def sv_min(self, b: float, fy: float, Asv: float) -> float:
        """Minimum spacing of shear reinforcement in a beam.
        Args:
            b (float): Width of the beam in mm.
            fy (float): Yield strength of the reinforcement in MPa.
            Asv (float): Area of shear reinforcement in mm².
        Returns:
            float: Minimum spacing of shear reinforcement in mm.
        """
        return Asv * fds * min(415, fy) / (0.4 * b)

    def nominal_cover_durability(self, exposure: Exposure, bardia: float, fck: float) -> float:
        """Nominal cover for durability based on exposure conditions.
        Args:
            exposure (Exposure): Exposure condition as defined in the Exposure enum.
            bardia (float): Bar diameter in mm.
            fck (float): Characteristic compressive strength of concrete in MPa.
        Returns:
            float: Nominal cover in mm.
        """
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
    """Class for detailing of slabs as per IS 456:2000.
    This class provides methods to calculate various parameters related to slab reinforcement,
    such as minimum and maximum reinforcement areas, bar diameters, spacing, and cover requirements.
    Attributes:
        None
    """

    def Ast_min(self, D: float, fy: float) -> float:
        """Minimum area of tension reinforcement in a slab.
        Args:
            D (float): Overall depth of the slab in mm.
            fy (float): Yield strength of the reinforcement in MPa.
        Returns:
            float: Minimum area of tension reinforcement in mm².
        """
        pst = 0.15 if fy < 415 else 0.12
        return pst / 100 * 1000 * D

    def Ast_max(self, D: float) -> float:
        """Maximum area of tension reinforcement in a slab.
        Args:
            D (float): Overall depth of the slab in mm.
        Returns:
            float: Maximum area of tension reinforcement in mm².
        """
        return Beam().Ast_max(1000.0, D)

    def bardia_max(self, D: float) -> float:
        """Maximum bar diameter for slab reinforcement.
        Args:
            D (float): Overall depth of the slab in mm.
        Returns:
            float: Maximum bar diameter in mm.
        """
        return D / 8.0

    def max_hor_spacing(self, d: float, main_bars: bool = True) -> float:
        """Maximum horizontal spacing of main reinforcement bars in a slab.
        Args:
            d (float): Effective depth of the slab in mm.
            main_bars (bool, optional): Whether the bars are main reinforcement bars. Default is True.
        Returns:
            float: Maximum horizontal spacing in mm.
        """
        if main_bars:
            return max(3 * d, 300.0)
        else:
            return max(5 * d, 450.0)

    def nominal_cover_durability(self, exposure: Exposure, bardia: float, fck: float) -> float:
        """Nominal cover for durability based on exposure conditions.
        Args:
            exposure (Exposure): Exposure condition as defined in the Exposure enum.
            bardia (float): Bar diameter in mm.
            fck (float): Characteristic compressive strength of concrete in MPa.
        Returns:
            float: Nominal cover in mm.
        """
        return Beam().nominal_cover_durability(exposure, bardia, fck)

    def nominal_cover_fire(self) -> float:
        """Nominal cover for fire resistance.
        Returns:
            float: Nominal cover in mm.
        Raises:
            NotImplementedError: This method is not implemented at present.
        """
        raise NotImplementedError


@dataclass
class Column:
    """Class for detailing of columns as per IS 456:2000.
    This class provides methods to calculate various parameters related to column reinforcement,
    such as minimum and maximum reinforcement areas, bar diameters, spacing, and cover requirements.
    Attributes:
        None
    """

    def Asc_min(self, b: float, D: float) -> float:
        """Minimum area of compression reinforcement in a column.
        Args:
            b (float): Width of the column in mm.
            D (float): Overall depth of the column in mm.
        Returns:
            float: Minimum area of compression reinforcement in mm².
        """
        return 0.8 / 100 * b * D

    def Asc_max(self, b: float, D: float) -> float:
        """Maximum area of compression reinforcement in a column.
        Args:
            b (float): Width of the column in mm.
            D (float): Overall depth of the column in mm.
        Returns:
            float: Maximum area of compression reinforcement in mm².
        """
        return 6 / 100.0 * b * D

    def bardia_min(self) -> float:
        """Minimum bar diameter for column reinforcement.
        Returns:
            float: Minimum bar diameter in mm.
        """
        return 12.0

    def lateral_ties_pitch(self, b: float, bardia_min: float) -> float:
        """Pitch of lateral ties in a column.
        Args:
            b (float): Width of the column in mm.
            bardia_min (float): Minimum bar diameter in mm.
        Returns:
            float: Pitch of lateral ties in mm.
        """
        return min(b, 16 * bardia_min, 300.0)

    def lateral_ties_dia(self, bardia_max: float) -> float:
        """Diameter of lateral ties in a column.
        Args:
            bardia_max (float): Maximum bar diameter in mm.
        Returns:
            float: Diameter of lateral ties in mm.
        """
        return max(bardia_max / 4.0, 6.0)
