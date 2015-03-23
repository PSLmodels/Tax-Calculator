Installation 
======================

While developing, you can install taxcalc including the most recent local changes via 

.. code-block:: python

	>>> python setup.py install 

For our latest deployed version, we keep the `latest version`_ for Python 2.7 and 3.4 under the ospc channel on binstar. To install 

.. code-block:: python

	>>> conda install -c ospc taxcalc

which will grab the latest taxcalc package from binstar.org. Currently, we host Python 3.4 packages for Linux and OS X. For contributors, the conda recipe is located in the ``conda.recipe`` directory. You can build the conda package via the ``conda build`` command:

.. code-block:: python 

	>>> conda build --python 3.4 conda.recipe/

To learn more about the conda package manager, go to the `conda docs`_.

.. _`conda docs`: http://conda.pydata.org
.. _`latest version`: https://binstar.org/ospc/taxcalc 
