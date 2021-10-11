# Materials
The primary materials in reinforced concrete are:

1. Concrete
2. Reinforcement bars
   1. Mild steel reinforcement bars with definite yield point
   2. High yield strength deformed bars with piece-wise linear stress-strain relation

## Concrete
The attributes of concrete that will be represented are:

1. `label`: A string representing a label. It will be used as a label in output
2. `fck`: Characteristic strength of concrete in N/mm$^2$
3. `gamma_m`: Partial safety factor for material, which is specified in IS&nbsp;456:2000 as 1.5
4. `density`: Density of concrete in kN/m$^3$
5. `stress_block`: Stress block specifying the stress-strain relation for concrete. This will depend on whether analysis or design is based on the Limit State Method&nbsp;(LSM) or Working Stress Method&nbsp;(WSM).


### Concrete Stress Block
Design or analysis of a section requires the determination of stress for a given strain. The stress-strain relation is different for the Limit State Method and Working Stress Method. While characteristic strength $f_{ck}$ remains the common parameter, LSM and WSM use different parameters to obtain the stress-strain relation.

## Reinforcement Bars
`Rebar` is an abstract class representing a bar of reinforcement. Reinforcement bars can be of different types, such as mild steel bars and high yield strength deformed (HYSD) bars. Both of them have some common attributes but have significantly different stress-strain relationships. The common attributes that will be available in all child classes are:

1. `label`: A string representing a label to refer to the type of reinforcement bar.
2. `fy`: Characteristic strength $f_{y}$ of the bar.
3. `gamma_m`: Partial safety factor for material, specifid by IS&nbsp;456:2000 to be $\gamma_m = 1.15$ for all types of reinforcement bars.
4. `density`: Density of steel, usually taken to be 78.5&nbsp;kN/m$^3$. This will be used to calculate the weight of steel reinforcement.
5. `Es`: Modulus of elasticity for steel, specifid by IS&nbsp;456:2000 to be $E_s = 2 \times 10^5$ for all types of reinforcement bars.

Reinforcement bars are specified as having a linear stress-strain relationship up to a certain point and stress is assumed to remain constant beyond yield up to infinity. While no material is truly infinitely ductile, if the ductile portion is sufficiently long in relation to permittion concrete to reach it ultimate strain, it would be sufficient to call it infinitely ductile.

### Mild Steel Reinforcement Bars
Mild steel reinforcement bars, represented by the `RebarMS` class, are known to have a well defined yield point and therefore have a distinct bilinear stress-strain relationship. This class does not need any additonal attributes beyond what is already defined in the parent `Rebar` class. It differs only in the stress-strain relationship. The stress is linear up to the yield stress and after yield, the stress is constant. Yield stress is $\frac{f_y}{\gamma_m} = \frac{f_y}{1.15} = 0.87 f_y$ and yield strain is $\frac{1}{E_s} \frac{f_y}{\gamma_m} = \frac{0.87 f_y}{2 \times 10^5}$.

### High Yield Strength Deformed Bars
High Yield Strength Deformed (HYSD) reinforcement bars, repesented by the `RebarHYSD` class, have a higher yield strength as implied by their name. `ReabHYSD` is derived from the abstract `Rebar` class. HYSD bars differ from mild steel bars in that they have a piece-wise linear stress-strain relationship. As per the Limit State Method&nbsp;(LSM) of IS&nbsp;456:2000, the stress-strain relation between the design stress of $0.8 \frac{f_y}{\gamma_m}$ and $\frac{f_y}{\gamma_m}$ is piece-wise linear and inelastic strain for each of the stress levels between 0.8 and 1.0 times $\frac{f_y}{\gamma_m}$, namely, 0.85, 0.9, 0.95 and 9.975 are specified as 0.0001, 0.0003, 0.0007, 0.001 and 0.002 respectively. From this information, it is possible to arrive at the complete stress-strain relation and determine the stress corresponding to a given strain. The only additional information required is the table of inelastic strains for the different levels of design stress.

## Layers of Reinforcement Bars
Reinforcement bars are placed in layers parallel to one of the principal axes of a section. The atrributes of a layer of reinforcement bars are:

1. `dia`: List of diameter of bars in the layer. It is assumed that all bars in a layer are of the same type.
2. `_dc`: Distance of the centroid of the layer from one of the edged of the section. If the distance is positive, it is interpreted as the distance from the highly compressed edge. If the distance is negative, it is interpreted as the distance from the tension edge. This assumes that the section has an edge parallel to one of the principal axes.
3. `_xc`: Distance of the centroid of the layer from the highly compressed edge. This value is calculated once the size of the section is known. It is _not_ an input.
4. `stress_type`: A string, 'C' if the layer is in compression and 'T' if it is tension. It is _not_ an input, but will be decided during analysis of the section in which the layer is located.


## Groups of Layers of Reinforcement Bars
Layers of reinforcement bars in a section are arranged in groups. For example, one layer near the compression edge and perhaps one or more near the tension edge. All layers are considered as part of a group of layers of reinforcement bars. Whether a particular layer of reinforcement bars within a group is subjected to tension or compression will only be known when the location of the neutral axis is computed. This is especially true of layers located close to the actual location of the neutral axis that is yet to be computed.

Attributes of a group of reinforcement bars are:

1. `rebar`: An object of type `Rebar` representing the type of reinforcement bar and its properties. Thus it is presumed that all bars in all layers of a group are of the same reinforcement type.
2. `layers`: List of objects of type `RebarLayer`. A group may have zero or more layers of reinforcement bars.

## Shear Reinforcement
Concrete, without any tension reinforcement has an ability to resist shear. However, when the shear force on a section exceeds the shear capacity of concrete, it will be necessary to either increase the depth of the cross section if that is an option, or to provide shear reinforcement to resist the additional shear beyond the capacity of concrete. Shear reinforcement can be provided in one of several ways:

However, there is an upper limit to the shear that can be resisted by a section with shear reinforcement. If the shear force on a section exceeds this limit, the only solution is to increase the depth of the cross section.

The `ShearReinforcement` is an abstarct class. The attributes of shear reinforcement are:

1. `rebar`: The type of reinforcement bars used as shear reinforcement.
2. `_Asv`: Area of shear reinforcement. This is _not_ an input data. It will be computed based on the type of reinforcement.
3. `_sv`: Spacing of shear reinforcement. This is an input data and is common for all types of shear reinforcement.

### Vertical and Inclined Stirrups
Reinforcement bars bent into the shape of a link and provided at a regular spacing can be used to resist shear force at a section. The `Stirrups` class is a child class of `ShearReinforcement`. While vertical bars make an angle of 90&nbsp;degree with the longitudinal axis of a beam, inclined stirrups usually make an angle of 45&nbsp;degree. The amount of shear resisted by a stirrup depends on the angle of the stirrup and increases as he angle approaches 90&nbsp;degree. The attributes of this type of shear reinforcement are:

1. `_nlegs`: Number of legs of the stirrup.
2. `_bar_dia`: Diameter of reinforcement bar used as stirrup.
3. `_alpha_deg`: Angle in degree made by the stirrup with the longitudinal axis of the beam. It is 90&nbsp;degree for vertical stirrups.


### Bent-up Bars
Bent-up bars used as shear reinforcement are the longitudinal tension bars that are bent up, usually at 45&nbsp;degree. Not all tension bars at midspan are required at the ends of a simply supported beam where the bending moment is very small. In the case of a fixed or continuous beam, tension is at the top edge and bottom bars are not required, unless they are used as compression bars. In any case, some bottom bars at midspan can be used as bent-up bars to augment shear capacity or can be curtailed if not used as shear reinforcement. It must be kept in mind that bent up bars are effective over a limited length of the beam. The attributes of bent-up bars as shear reinforcement are:

1. `bars`: List of diameters of bars that are bent-up. This can be subset of a layer of reinforcement that will be bent up.
2. `_alpha_deg`: Angle in degrees made by the bent-up bars with the longitudinal axis of the beam.
