Software Design
===================
This project has adopted the Object Oriented Programming (OOP) approach to design and implement a set of classes and class hierarchies to represent the important components of reinforced concrete sections and structural elements. This approach is well suited to the problem at hand for several reasons:

1. The concepts of data encapsulation is very helpful since each entity has several attributes and passing an object of a specific class automatically carries its state in a single object. This greatly reduces the number of arguments that would have to be passed to functions if it were to be implemented using the procedural programming paradigm.
2. The concept of abstract classes and inheritance repesents the relation between entities such as a rectangular beam section and a flanged beam section which are concrete types of the abstract class representing a section. Similar relation exists between mild steel reinforcement bar and HYSD bar which are concrete classes of the abstract class representing a reinforcement bar. Similarly, vertical stirrups, inclined stirrups and bent-up bars are concrete classes of the abstract class representing shear reinforcement.
3. The concept of composition, where a class is a synthesis of several components directly represents a class such as a section that consists of concrete, main reinforcement bars and shear reinforcement bars, in addition to the attributes of a section such as its dimensions.

This package therefore consist of several abstract and concrete classes, at present, to represent the following:

1. Concrete stress block
2. Concrete
3. Reinforcement bars - Mild steel reinforcement bars and HYSD reinforcement bars
4. Reinforcement concrete section, Rectangular beam section, flanged beam section and rectangular column section

Since it is decided to begin with analysis, the methods that are being implemented at present will aim to determine the limit state capacity of the different sections, such as :math:`M_u` and :math:`V_u` for beam sections and :math:`P_u` and :math:`M_u` for column sections, given the exact dimensions, material and reinforcement details.

Classes
-----------

The following classes have been implemented:

1. A class **LSMStressBlock** to represent the stress block for concrete in compression under limit state of flexure, as well as limit state of combined axial compression and flexure as per IS 456:2000.
2. A class **Concrete** to represent concrete.
3. An abstract class **Rebar** to represent reinforcement bars. Two derived classes **RebarMS** and **RebarHYSD** to represent mild steel bars and high yield strength deformed bars, respectively.
4. A class **RebarLayer** to represent a single layer of reinforcement bars, defined as a list of bar diameters and the distance of the centre of the bars from the nearest edge. A class **RebarGroup** to represnt a list of layers of reinforcement bars.
5. An abstract class **ShearReinforcement** to represent shear reinforcement. Two derived classes **Stirrups** and **BentupBars** to represent vertical/inclined stirrups and bent up bars, respectively.
6. A class **ShearRebarGroup** to represent a group of shear reinforcement bars.
7. A class **RectBeamSection** to represnt a reinforced concrete rectangular beam section. A derived class **FlangedBeamSection** to represnt flanged sections subejcted to flexure and shear, derived from **RectBeamSection**.
8. A class *RectColumnSection** to represent a reinforced concrete rectangular coulmn section subjected to combined axial compression and bending about one axis.

Methods
------------

Following funcationality has been implemented for the different classes:

1. **LSMStressBlock**: Calculation of the following:

    * strain distribution,
    * stress for a given strain,
    * stress at a specified distance :math:`x` from neutral axis,
    * area of stress distribution between two locations :math:`x_1` and :math:`x_2` from neutral axis, and
    * moment of stress block between the two locations with respect to depth :math:`x_u` of the neutral axis.

    These are implemented for the following cases:

    * Flexure
    * Combined axial compression and bending about one axis.

2. **Concrete**: Calculation of design stress :math:`f_d`, shear stress :math:`\tau_c` and maximum shear stress :math:`\tau_{c,max}`.
3. **RebarMS** and **RebarHYSD**: Stress for a specified value of strain and design stress.
4. **RebarLayer**: Area of bars in a layer.
5. **RebarGroup**: Calculation of the sum of the following values aggregated after calculating the values individually for each layer:

    * Area of reinforcing bars in the group,
    * Force in reinforcing bars in the group, in tension and in compression,
    * Moment of force in reinforcing bars in the group about the neutral axis, in tension and in compression

6. **RectBeamSection** and **FlangedBeamSection**:
   Calculation of:

    * Total compression force and the corresponding moment about the neutral axis for a specified neutral axis location :math:`x_u`, considering concrete in compression and compression reinforcement bars, if present,
    * Total tension force and the corresponding moment about the neutral axis due to a group of tension reinforcement bars,
    * Position of the neutral axis :math:`x_u`, calculated iteratively to satisfy equilibrium,
    * Shear force capacity of a section for a given shear reinforcement in the form of vertical or inclined stirrups,
    * Spacing of vertical or inclined stirrups for a given design shear force
7. **RectColumnSection**: Calculation of:
    * Total axial compression force and bending moment about the neutral axis for a given position of the neutral axis.