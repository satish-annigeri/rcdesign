from rcdesign.is456.material.concrete import ConcreteLSMFlexure, Concrete
from rcdesign.is456.material.rebar import (
    BentupBars,
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection

rsec = RectBeamSection(
    230,
    450,
    Concrete("M20", 20, ConcreteLSMFlexure("IS456 LSM")),
    RebarGroup(
        RebarHYSD("Fe 415", 415),
        [RebarLayer([16, 16], 35), RebarLayer([20, 20, 20], -35)],
    ),
    ShearRebarGroup([Stirrups(RebarHYSD("Fe 415", 415), 2, 8, 150)]),
    25,
)
# print(rsec)
print()
# print(
#     rsec.long_steel.report(
#         100,
#         Concrete("M20", 20, ConcreteLSMFlexure("IS456 LSM")),
#         RebarHYSD("Fe 415", 415),
#         0.0035,
#     )
# )
# print()

tsec = FlangedBeamSection(
    230,
    450,
    1000,
    150,
    Concrete("M20", 20, ConcreteLSMFlexure("IS456 LSM")),
    RebarGroup(
        RebarHYSD("Fe 415", 415),
        [RebarLayer([16, 16], 35), RebarLayer([20, 20, 20], -35)],
    ),
    ShearRebarGroup(
        [
            Stirrups(RebarHYSD("Fe 415", 415), 2, 8, 150),
            BentupBars(RebarHYSD("Fe 415", 415), [16, 16], _sv=250),
        ]
    ),
    25,
)
# print(tsec)

print(rsec.report(120, 0.0035))
# print(tsec.report(40, 0.0035))
