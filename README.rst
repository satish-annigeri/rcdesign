=========================================================================================
Python package for analysis and design of reinforced concrete sections as per IS 456:2000
=========================================================================================
This is a Python package for analysis and design of reinforced concrete sections as per IS 456:2000, the Indian Standard code of practice for plain and reinforced concrete. All units are Netwon and millimeter. The intention is to devlop packages to represent materials, stress blocks, rebars, sections, and other components essential to analyse and design reinforced concrete sections. It is initally planned to carry out analysis of sections before taking up design of sections. Initially, analysis of beam sections, specifically rectangular and flanged sections will be taken up for flexure and shear. Analysis of rectangular column sections will be taken up next.

The intention is to progress to design and detailing of beams and columns subsequent to the completion of analysis and design of sections. Object oriented programming is particularly well suited from problems such as this as inheritance and composition are natural in the representation of structures, their components and material and their behaviours.

At present limit state analysis of rectangular sections for flexure is underway. The following have been implemented:

1. Class to represent the stress distribution in concrete as per IS 456:2000
2. Class to rerpresent concrete and reinforcement bars
3. Class to represent layer of reinforcement bars
4. Class to represent a group of layers of reinforcement bars
5. Class to represent rectangular sections subjected to flexure and shear

Code has been completed to carry out analysis of a rectangular section with given size, materials and reinforcement placement. Locating the position of neutral axis for ultimate strain in concrete at the highly compressed edge to satisfy equilibrium for the case when reinforcement bars are located in both the tension and compression regions of the section. For any assumed location of the neutral axis and ultimate strain at the highly compressed edge, including the location corresponding to equilibrium, is complete. Iteratively converging on the neutral axis location corresponding to equilibrium is done using bisection method.

The concrete stress block definition is associated with concrete material and is inherited from an abstract class to represent a general stress block. Therefore, replacing the stress block definition with any other is possible by sub-classing the abstract stress block class while keeping all the rest of the procedures unchanged.

The rectangular beam section class is inherited from rectangular beam section class. Similarly, it should be possible to compose beams, columns as a collection of sections and a structure as a collection of beams and columns.

The package is in early development and is yet to undergo systematic testing. There is no documentation at the current time.
