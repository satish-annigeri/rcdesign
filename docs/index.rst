.. rcdesign documentation master file, created by
   sphinx-quickstart on Tue May 20 17:09:06 2025.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Documentation for ``rcdesign``
===============================

.. image:: https://img.shields.io/github/license/satish-annigeri/rcdesign
   :alt: License
   :target: https://github.com/satish-annigeri/rcdesign/blob/main/LICENSE

.. image:: https://img.shields.io/pypi/v/rcdesign
   :alt: PyPI Version
   :target: https://pypi.org/project/rcdesign/

.. image:: https://img.shields.io/readthedocs/rcdesign
   :alt: Documentation Status
   :target: https://rcdesign.readthedocs.io/en/latest/

.. image:: https://img.shields.io/pypi/dm/your-package
   :alt: PyPI Monthly Downloads
   :target: https://pypi.org/project/rcdesign/

.. image:: https://img.shields.io/badge/code%20style-Ruff-blue
   :alt: Code Style: Ruff
   :target: https://github.com/astral-sh/ruff

.. image:: https://img.shields.io/github/downloads/satish-annigeri/rcdesign/total
   :alt: GitHub Downloads
   :target: https://github.com/satish-annigeri/rcdesign/releases



.. toctree::
   :maxdepth: 1
   :caption: Contents

   installation
   quickstart
   theory
   api

``rcdesign`` is a Python package for analysis of reinforced concrete (RC) sections as per the limit state method (LSM) of IS 456:2000 - the code of practice for plain and reinforced concrete in India.

Current Status
----------------

The package is in early development and may undergo backward incompatible changes. It has undergone testing of the current code base. Limited examples have been solved and verified by hand. Test coverage is currently 100% (exccluding the example script).

What ``rcdesign`` can and cannot do
-----------------------------------

At present ``rcdesign`` **can do** the following:

1. Represent stress strain relationship for:
    1. concrete in flexure as per IS 456:2000 (38.1),
    2. concrete under axial compression and flexure as per IS 456:2000 (39.1),
    3. reinforcement bars:
        1. mild steel bars with well defined yield point
        2. cold worked deformed bars
2. Represent layers of reinforcement bars placed parallel to the edge of the section at a given distance from the compression (or tension edge). Bars can be of different diameters but must be of the same type.
3. Represent group of layers of reinforcement bars. All bars in a group must be of the same type, although their diameters may differ, and layers of reinforcement must be placed parallel to the short edge _b_ of the section.
4. Represent group of shear reinforcement in the form of vertical stirrups, inclined stirrups and bent-up bars.
5. Analyse reinforced concrete rectangular and flanged sections subjected to bending and shear as per the Limit State Method according to IS 456:2000, the Indian standard code of practice for plain and reinforced concrete. This calculates the ultimate strength of the section in bending and shear depending on the materials, section size and main (longitudinal) and shear reinforcement.
6. Analyses reinforced concrete rectangular sections subjected to axial compression and bending about one axis parallel to the first (usually the short) edge, as per limit state method of IS 456:2000.

Rectangular and flanged sections must be of a given grade of concrete. Main (longitudinal) reinforcement to resist bending must be provided as a single group of reinforcement layers, arranged in one or more layers. Depending on their distance from the compression edge, the layers of rebars may lie in the tension and/or compression zone of the section.However, since the position of the neutral axis is dependent on the section size and the amount and location of main reinforcement, whether a layer of reinforcement lies in the tension zone or the compression zone will be known only after an analysis of the section.

At present, ``rcdesign`` **cannot do** the following:

1. Cannot design sections, either for bending, shear and torsion or for axial compression with or without bending about one or both axes.
2. Cannot verify whether the section meets the detailing requirements of IS 456:2000 (26).
3. Cannot analyse or design sections as per Working Stress Method of IS 456:2000 (Annexure N).
4. Cannot design reinforced concrete elements such as beams and columns. At present, the scope of the package is restricted to analysis and design of sections of beams and columns. Design of sections is a distant goal, but no promises.

Some or all of the above features will be gradually added. Contributions in accomplishing this are welcome.

Contribute
----------------

Contributions are welcome. Contributions can be in a variety of forms:

1. Bug reports
2. Additional features
3. Documentation
4. Additional examples

Links
----------------

- Documentation: [``rcdesign`` on Read the Docs](https://rcdesign.readthedocs.io/en/latest/)
- PyPI release: [![PyPI version shields.io](https://img.shields.io/pypi/v/rcdesign)](https://pypi.python.org/pypi/rcdesign/)
- Github repository: https://github.com/satish-annigeri/rcdesign

Documentation
~~~~~~~~~~~~~~~~~~~

[Documentation is available here](https://rcdesign.readthedocs.io/en/latest/). Any advise or help on improving the documentation is welcome.

Future Plans
-------------

Immediate plans include the design of *sections*:

1. Design of rectangular and flanged sections subjected to bending, shear and torsion.
2. Write user and API documentation using Sphinx.
3. Design of rectangular column *sections*.
4. Detailing of rectangular beam *sections* subjected to bending, shear and torsion.
5. Design of rectangular column *sections* subjected to combined axial compression and bending.
6. Implementing a stress block to represent *working stress method*.

Long term plans include:

1. Design and detailing of reinforced concrete elements such as beams, columns, slabs, footings, retaining walls etc.
2. Calculation of deflections of elements.
3. Design and detailing of reinforced concrete structures, including detailing of joints (very far into the future, if at all).

References
----------
1. IS 456:2000 Indian Standard Code of Practice for Plain and Reinforced Concrete (Fourth Revision), Bureau of Indian Standards, New Delhi, 2000.
2. SP:24 (S&T)-1983 Explanatory Handbook on Indian Standard Code of Practice for Plain and Reinforced Concrete (IS 456:1978), Bureau of Indian Standards, New Delhi, 1984.
3. SP 16:1980 Design Aids for Reinforced Concrete to IS:456-1978, Bureau of Indian Standards, New Delhi, 1980.

.. |nbsp| unicode:: U+00A0
   :trim: