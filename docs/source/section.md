# Sections
Reinforced concrete structures are made of reinforced concrete structural members. They can be broadly classified into:

1. **Beams** which are predominantly subjected to bending, shear and torsion, and
2. **Columns** which are predominantly subjected to axial compression, possibly with an accompanying bending moment.

Strctural members where both bending and axial compression forces are equally dominant are called beam-columns. Analysis and design of beams is simpler and bending and shear actions can be treated independently. Analysis and design of sections subjected only to axial compression is also simple.

Analysis of sections subjected to axial compression and bending about one axis is a coupled problem. That is, for a given section, materials, reinforcement, and chosen location of neutral axis, there is a unique pair of axial compression $P_u$ and bending $M_u$ about one axis. But changing the location of the neutral axis results in a different combination of $P_u$ and $M_u$.

Design of such sections is carried out as an inverse step of carrying out a large number of analyses and choosing the combination nearest to the given design forces. Usual practice is to construct interaction diagrams for different amounts of longitudinal reinforcement and plotting an interaction diagram for each value of area of longitudinal reinforcement.

## Beam Sections
A beam section can have any shape but from the point of view of ease of fabrication and aesthetics, rectangular beam section is the most common. The attributes, required to repesent a section irrespective of whether it belongs to a beam or a column, are listed below:

1. `csb`: Object of type concrete stress block repesenting strain distribution and stress stran relation for flexure.
2. `conc`: Object of type `Concrete`. There must only be one object of this type associated with a given section.
3. `long_steel`: Object of type `RebarGroup` representing the longitudinal reinforcement provided along the length of the structural member. There must only be one object of this type associated with a given section.
4. `shear_steel`: A list of objects of type shear reinforcement, consisting of zero or more of vertical or inclined stirrups, or bent-up bars.
5. `clear_cover`: Clear cover to reinforcement bars. 

Effective section of a beam can be rectangular or flanged. Since reinforced concrete slab is cast together with beams, the effective shape of the section is a flanged section if the slab happens to be in the compression zone or rectangular if the slab happens to be in the tension zone. A flanged section can be a T section with the flange extending on both sides of the web (as in the case of an intermediate beam) or an L section with the flange extending on only one side (as in the case of an end beam). Typically, mid-span section under gravity loads is subjected to sagging bending moment and the slab is in the compression zone resulting in a flanged section. But end sections are subjected to hogging bending moment and the slab is in the tension zone resulting in a rectangular section. Based on the bending moment distribution, section can be categorized as rectangular or flanged.

### Rectangular Beam Sections
The `RectBeamSection` class is derived from the `Section` abstract class. Being a beam section, it is expected to be subjected to bending, shear and torsion. Additional attributes of a `RectBeamSection` in addition to those already defined in the parent class `Section` are:
1. `b`: Breadth of the beam, in mm
2. `D`: Overall depth of the beam, in mm
3. `shear_steel`: Object of type `ShearRebarGroup`, containing a list of one or more shear reinforcement types.


### Flanged Beam Sections
The `FlagnedBeamSection` is a derived class of `RectBeamSection` and has all its atributes and many of its behaviours. Additional attributes of a `FlangedBeamSection`, in addition to those already defined in the parent class `RectBeamSection` are:

1. `bf`: Breadth of the flange, in mm
2. `Df`: Depth of the flange, in mm


## Column Sections
TO DO

