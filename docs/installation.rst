Installation
=================

Python Version
-----------------

The package is developed and tested with Python 3.12. It is recommended to use the latest version of Python 3.12 or later. The package may work with earlier versions of Python 3, but it is not guaranteed.

Dependencies
-----------------
The package requires the following packages:

* numpy
* sympy

Optional Dependencies
---------------------------

These packages will not be installed automatically. They are required only when wish to run tests, look at and modify the source code or generate documentation. They are not required for using the package. The optional dependencies are arranged in two separate groups.

* Development dependencies
    * pytest
    * pytest-cov
    * nox
    * ruff
* Documentation dependencies
    * sphinx
    * sphinx_rtd_theme
    * sphinx-tabs

This project uses ``uv`` to manage the project. This documentation therefore uses ``uv`` command line instructions, See here for `instructions to install <https://docs.astral.sh/uv/>`_ ``uv``.

Install from PyPI using ``pip``
--------------------------------

This is when you only wish to use ``rcdesign`` without attempting to look at its source code, documentation on your local machine or wishing to run tests.

The traditional way is to install ``rcdesign`` from PyPI using ``pip`` into a previously created virtual environment and write your scripts to use the package. The other way is to use ``uv`` to create the virtual environment and install ``rcdesign`` from PyPI using ``uv``. The former approcah is good enough if you merely wish to use the package, and that is described below. If you wish to explore the source code, generate the documentation and run tests on your local machine, it is better to take the latter approach, and that is described in the next section.

Requirements
~~~~~~~~~~~~

* Python >= 3.12+
* numpy
* sympy

Install from PyPI
~~~~~~~~~~~~~~~~~~~~~~~

Create a separate directory and create a virtual environment. Activate the virtual environment and install required packages. First, choose the directory where you wish to create your project and change into that directory. On \*nix systems, do the following:

.. tabs::

   .. group-tab:: Linux/macOS

      .. code-block:: bash

            $ mkdir rcd_tutorial
            $ cd rcd_tutorial
            $ python -m venv .venv
            $ source .venv/bin/activate
            (.venv)$ pip install rcdesign
            (.venv)$ python run -c "from rcdesign import __version__; print(__version__)"
    
   .. group-tab:: Windows

      .. code-block:: bash

            > mkdir rcd_tutorial
            > cd rcd_tutorial
            > python -m venv .venv
            > .venv\Scripts\activate
            (.venv)$ pip install rcdesign
            (.venv)$ python run -c "from rcdesign import __version__; print(__version__)"

   .. group-tab:: uv

      .. code-block:: bash

         > mkdie rcd_tutorial
         > cd rcd_tutorial
         > uv init --bare
         > uv add rcdesign
         > uv run -- python -c "from rcdesign import __version__; print(__version__)"

Install using:

.. code-block:: text

    (.venv)$ pip install -U rcdesign
    (.venv)$ python -c "from rcdesign import __version__;print(__version____)

This prints the release version and it must match the version displayed by the ``pip list`` or ``uv pip list`` (if you are using ``uv``) command.

Run the two built-in example problems and study the output.

.. code-block:: text

    (.venv)$ python -m rcdesign

See :doc:`quickstart` for more details on how to use the package. You can also run the examples in the ``tests`` directory with the command:

Install from Source on GitHub
-------------------------------------

Installing source code from GitHub is for those interested in exploring the source code to understand how the code works and possibly remove bugs and/or make improvements.

Clone the repository
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Choose a suitable directory where you wish to clone the source code from github.  Clone the repository using ``git``

.. code-block:: text

    $ git clone https://github.com/satish-annigeri/rcdesign.git

This creates a new directory named ``rcdesign`` in the current working directory. Change over to the directory ``rcdesign`` that is created with the command

.. code-block:: text

    $ cd rcdesign

List the directory contents and verify the directory structure.

Install required packages
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Using ``uv`` for project management simplifies the process. Therefore install ``uv`` before starting with the steps below. Note however, that using ``uv`` is not essential, but the steps to do so are not described here. However, the project uses ``pyproject.toml``, installing required packages using ``pip`` should be straight forward. **Note:** It is not required to activate the virtual environment if you use ``uv``.

Install required packages into the virtual environment with ``uv``

.. code-block:: text

    $uv sync

This will create the virtual environment ``.venv`` if it does not already exust. It will also install all the required packages listed in ``pyproject.toml``.

If you wish to run tests, you can install the additional dependenies with the command:

.. code-block:: text

    $ uv sync --dev

This will install ``pytest`` and ``pytest-cov`` required to run the tests.

Run tests
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the tests with ``pytest``

.. code-block:: text

    $ uv run pytest tests

Check code coverage.

.. code-block:: text

    $ uv run pytest --cov=src --cov-report=html tests

Testing and Code Coverage Status
----------------------------------------------

Testing  has been implemented using ``pytest`` and unit tests have been implemented for the following classes:

1. **ConcreteLSMFlexure** and **Concrete**
2. **RebarMS** and **RebarHYSD**
3. **RebarLayer** and **RebarGroup**
4. **ShearReinforcement** and **Stirrups**
5. **RectBeamSection** and **FlangedBeamSection**
6. **RectColumnSection**

Code coverage through tests using ``pytest-cov`` at the current time is 100%, excepting the example script and the methods that implement ``__repr__()`` and ``report()``.

Analysis of rectangular and flanged beam sections with and without compression reinforcement, for flexure and shear, has been completed. Several examples have been solved and verified by hand to consider different cases.

Analysis of rectangular column sections for combined axial compression and bending about one axis has been completed. An example has been solved and verified by hand.

Examples
-----------------

Built-in Examples
~~~~~~~~~~~~~~~~~~~~~

Run the built-in example with the following command.

.. code-block:: text

    $ uv run rcdesign

Examples from ``tests`` Directory
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Run the additional examples in the ``tests`` directory with the following command from the command prompt:

.. code-block:: text

    $ uv run python -m tests.example01
    $ uv run python -m tests.example02
    ...
    $ uv run python -m tests.example09

To try your own examples, see: :doc:`quickstart`.
