# Theory

## Introduction

Reinforced concrete is, along with steel, a widely used structural material in the construction of buildings, bridges and other such structures. The primary tasks for a structural engineer working with reinforced concrete are design and analysis.

Design aims to proportion the section size and determine the reinforcement required to resist a given set of design forces. For a beam section, design foces constitute bending moment, shear force and torsional moment. For a column section, design forces constitute axial compression and bending moment about one or both major axes.

Analysis involves determining the capacity of a given section with known dimensions and reinforcement details. For a beam section, capacity in bending and shear are computed. For a column section, the pair of axial compression and bending moment about one axis are computed.

Be it design or analysis, it is first necessary to work at the section level and subsequntly carry out design or analysis of the entire structural element, such as a beam or a column. The design of a beam or a column can be treated as the design of a series of sections at critical locations. Similarly, analysis of a structural element, such as a beam or a column, requires the calculation of the capacity of sections at critical locations.

Design and analysis complement each other. When we design, the intention is that the designed section must have a capacity equal to or greater than the imposed design forces. However, the actual capacity of the section after design is rarely computed and the over-strength of the designed section is usually not known. The analysis of a section results in the calculation of the capacity of the section. Comparing the capacity with the actual design forces that are known to act at the section help us in deciding whether the section is safe or unsafe and also in determining the strength ratio - the ratio of the capacity of the section to the design force imposed on the section.

In this work, the task of analysis of a section is taken up first even though the more common task is that of design. That is because, analysis is more precise compared to design, which requires adjusting quantities upwards, such as the depth of the section (because it is preferred to provide dimensions that are practical for fabrication) or the number of reinforcement bars to be provided (because it is not possible to provide fraction of a bar). Moreover, analysis does not involve the task of detailing, such as ensuring the horizontal distance between bars is greater than the prescribed minimum, checking if the required number of reinforcement bars will fit within the breadth of the beam and adjusting them in multiple layers if they do not all fit in a single layer etc. This makes analysis simpler than design.

The task of design can be broken down into determining the required section dimensions, reinforcement bars, satisfying detailing requirements and finally calculating the capacity of the section and computing the strength ratio. Thus, completing the task of analysis first aids the task of design.


- [Software Design](software_design.md)
- [Materials](materials.md)
- [Sections](section.md)
