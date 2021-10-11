# Sections
Reinforced concrete structures are made of reinforced concrete structural members. They can be broadly classified into:

1. **Beams** which are predominantly subjected to bending, shearand torsion, and
2. **Columns** which are predominantly subjected to axial compression possibly with an accompanying bending that is small compared to the axial compressive force.

Strctural members where both bending and axial compression forces are equally dominant are called beam-columns. Analysis and design of beams is simpler and bending and shear actions can be treated independently. Analysis and design purely for axial compression is also simple and straight forward. Analysis of sections subjected to axial compression and bending about one axis is a coupled problem, in that, for a given section and reinforcement, there is a unique pair of axial compression and bending about one axis. Design of such sections is carried out as an inverse step of carrying out a large number of analyses and choosing the combination nearest to the given design forces. Usual practice is to construct interaction diagrams for different amounts of compression reinforcement and plotting an interaction diagram for each area of compression reinforcement.

## Beam Sections
A beam section can have any shape but from the point of view of ease of fabrication and aesthetics, rectangular beam section is the most common. The attributes, required to repesent a section irrespective of whether it belongs to a beam or a column, are listed below:

1. `conc`: Object of type `Concrete`. There is only one object of this type associated with a given section.
2. `main_steel`: Object of type `RebarGroup` representing the main reinforcement provided along the length of the structural member. At present, there is only one object of this type associated with a given section.
3. `clear_cover`: Clear cover to reinforcement bars. 

Since reinforced concrete slabs are cast together with beams, the effective shape of the section is a flanged section if the slab happens to be in the compression zone or rectangular if the slab happens to be in the tension zone. A flanged section can be a T section with the flange extending on both sides of the web (as in the case of an intermediate beam) or an L section with the flange extending on only one side (as in the case of an end beam).

### Rectangular Beam Sections
The `RectBeamSection` class is derived from the `Section` abstract class. Being a beam section, it is expected to be subjected to bending, shear and torsion. Additional attributes of a `RectBeamSection` in addition to those already defined in the parent class `Section` are:
1. `b`: Breadth of the beam, in mm
2. `D`: Overall depth of the beam, in mm
3. `shear_steel`: Shear reinforcement, one of `Stirrups` or `BentupBars`. At present, only one object of this type is associated with a given section. This may change in future.


### Flanged Beam Sections
The `FlagnedBeamSection` is a derived class of `RectBeamSection` and has all its atributes and many of its behaviours. Additional attributes of a `FlangedBeamSection` in addition to those already defined in the parent class `RectBeamSection` are:

1. `bf`: Breadth of the flange, in mm
2. `Df`: Depth of the flange, in mm


## Column Sections
TO DO

### Rectangular Sections

TO DO