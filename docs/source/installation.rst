Installation 
======================

The taxcalc package is installable via 

.. code-block:: python

	>>> python setup.py install 

We currently test against Python 2.7 and 3.4. You can install the latest conda package via

.. code-block:: python

	>>> conda install -c ospc taxcalc

which will grab the latest taxcalc package from binstar.org. Currently, we host Python 3.4 packages for Linux and OS X. For contributors, the conda recipe is located in the ``conda.recipe`` directory. You can build the conda package via the ``conda build`` command:

.. code-block:: python 

	>>> conda build --python 3.4 conda.recipe/

To learn more about the conda package manager, go to the `conda docs`_.



.. _`conda docs`: conda.pydata.org 
