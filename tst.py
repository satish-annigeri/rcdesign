from rcdesign.is456.stressblock import LSMStressBlock
from rcdesign.is456.concrete import Concrete
from rcdesign.is456.rebar import (
    BentupBars,
    RebarHYSD,
    RebarLayer,
    RebarGroup,
    Stirrups,
    ShearRebarGroup,
)
from rcdesign.is456.section import RectBeamSection, FlangedBeamSection


def print_dict(LD):
    hdr = ""
    for k, v in LD[0].items():
        hdr += f" {k}"
    hdr = (hdr + " ").replace(" ", "|")
    s = f"{hdr}\n"
    for L in LD:
        s += f"{L['fy']:6.0f} {L['Bars']:>12} {L['xc']:8.2f} {L['Strain']:12.8f} {L['Type']:>4} {L['f_s']:8.2f} {L['f_c']:6.2f} {L['F']/1e3:8.2f} {L['M']/1e6:8.2f}\n"
    print(s, end="")


rsec = RectBeamSection(
    230,
    450,
    LSMStressBlock(),
    Concrete("M20", 20),
    RebarGroup(
        [
            RebarLayer(RebarHYSD("Fe 415", 415), [16, 16], 35),
            RebarLayer(RebarHYSD("Fe 415", 415), [20, 20, 20], -35),
        ],
    ),
    ShearRebarGroup([Stirrups(RebarHYSD("Fe 415", 415), 2, 8, 150)]),
    25,
)
print(rsec.report(120, 0.0035))
LD = [
    rsec.long_steel.layers[0].asdict(120.0, LSMStressBlock(), Concrete("M20", 20)),
    rsec.long_steel.layers[1].asdict(120.0, LSMStressBlock(), Concrete("M20", 20)),
]

print_dict(LD)
# print(
#     rsec.long_steel.report(
#         100,
#         Concrete("M20", 20, ConcreteLSMFlexure("IS456 LSM")),
#         RebarHYSD("Fe 415", 415),
#         0.0035,
#     )
# )
# print()

# tsec = FlangedBeamSection(
#     230,
#     450,
#     1000,
#     150,
#     Concrete("M20", 20, ConcreteLSMFlexure("IS456 LSM")),
#     RebarGroup(
#         RebarHYSD("Fe 415", 415),
#         [RebarLayer([16, 16], 35), RebarLayer([20, 20, 20], -35)],
#     ),
#     ShearRebarGroup(
#         [
#             Stirrups(RebarHYSD("Fe 415", 415), 2, 8, 150),
#             BentupBars(RebarHYSD("Fe 415", 415), [16, 16], _sv=250),
#         ]
#     ),
#     25,
# )
# print(tsec)

# print(tsec.report(40, 0.0035))
