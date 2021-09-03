# Python package for analysis and design of reinforced concrete sections as per IS 456:2000

This is a Python package for analysis and design of reinforced concrete sections as per IS 456:2000, the Indian Standard code of practice for plain and reinforced concrete. All units are Netwon and millimeter.

## Objective

The objective is to devlop a package to represent materials, stress blocks, rebars, sections, and other components essential to analyse and design reinforced concrete sections. It is initally planned to carry out analysis of sections before taking up design of sections as per the limit state method of IS 456:2000.

Object oriented programming is particularly well suited from problems this nature as inheritance and composition are natural in the representation of structures, their components, and materials as well as their behaviours. Further, speed of execution is not a primary concern, as it is in the analysis of structures.

In the beginning, analysis of beam sections - rectangular and flanged sections, will be taken up for flexure and shear. Analysis of rectangular column sections will be taken up subsequently.

The package will consist of a hierarchy of classes along with their methods to implement analysis, design and detailing at the section level.

## Current Status

The package is in early development and has undergone limited testing. No documentation is available at the current time.

The following classes have been implemented:

1. An abstract base class **StressBlock** to represent a stress block.
2. A derived class **ConcreteStressBlock** to represent the stress block for concrete in compression under limit state of flexure, derived from the abstract StressBlock class.
3. A class **Concrete** to represent concrete which consists of a ConcreteStressBlock.
4. An abstract class **Rebar** to represent reinforcement bars. Two derived classes **RebarMS** and **RebarHYSD** to represent mild steel bars and high yield strength deformed bars, respectively.
5. A class **RebarLayer** to represent a single layer of reinforcement bars. A class **RebarGroup** to represnt a group of layers of reinforcement bars.
6. An abstract class **ShearReinforcement** to represent shear reinforcement. Two derived classes **Stirrups** and **BentupBars** to represent vertical or inclined stirrups and bent up bars, respectively.
7. An abstract class **Section** to represnt a cross section. Two derived classes **RectBeamSection** and **FlangedBeamSection** to represnt rectangular and flanged sections subejcted to flexure and shear.

Following funcationality has been implemented for the different classes:

1. **ConcreteStressBlock**: Calculation of design stress, stress at a specified distance $x$ from neutral axis, area of stress block between two locations $x_1$ and $x_2$ from neutral axis and moment of stress block between the two locations with respect to depth $x_u$ of the neutral axis.
2. **RebarMS** and **RebarHYSD**: Stress for a specified value of strain and design stress.
3. **RebarLayer**: Area of bars in a layer.
4. **RebarGroup**: Calculation of the sum of the following values aggregated after calculating the values individually for each layer:
    * Area of reinforcing bars in the group,
    * Force in reinforcing bars in the group, in tension and in compression,
    * Moment of force in reinforcing bars in the group about the neutral axis, in tension and in compression
5. **RectBeamSection** and **FlangedBeamSection**: Calculation of:
    * Total compression force and the corresponding moment about the neutral axis for a specified neutral axis location $x_u$, considering concrete in compression and compression reinforcement bars, if present,
    * Total tension force and the corresponding moment about the neutral axis due to a group of tension reinforcement bars,
    * Position of the neutral axis $x_u$, calculated iteratively to satisfy equilibrium,
    * Shear force capacity of a section for a given shear reinforcement in the form of vertical or inclined stirrups,
    * Spacing of vertical or inclined stirrups for a given design shear force

## Future Plans

Immediate plans include the analysis and design at the *section* level:

1. Analysis of rectangular *section* subjected to axial compression and bending about one axis.
2. Design of rectangular and flanged *sections* subjected to bending, shear and torsion.
3. Design of column *sections*.
4. Detailing of sections subjected to bending, shear and torsion.

Long term plans include design and detailing of elements:

1. Reinforced concrete elements such as beams and columns.
2. Reinforced concrete structures including detailing of joints (very far into the future, if at all).

