Micro Data
==========

The Tax-Calculator simulates federal individual income and FICA
taxes for each tax filing unit in a sample. For revenue
estimation, that sample must be representative of the US
population. 

Description
-----------

This project commonly relies on a micro dataset that closely reproduces
the multivariate distribution of income, deduction and credit items in
2009, extrapolated to 2015-2026 levels in accordance with
`CBO forecasts`_ available in Spring 2016. It is intended to match similar
but confidential data used by the Congressional Joint Committee on
Taxation. The underlying dataset must be purchased from the Statistics
of Income division of the Internal Revenue Service. Additional
information on non-filers is taken from the March 2013 Current
Population Survey. 

The open source `TaxData`_ model implements the extrapolation and statistical
match. 



Documentation
-------------

For additional documentation on the core variables used by the Tax
Calculator, refer to the `general description booklet`_.


.. _`CBO forecasts`: https://www.cbo.gov/publication/51129
.. _`general description booklet`: http://users.nber.org/~taxsim/gdb/gdb09.pdf
.. _`TaxData`: http://www.github.com/open-source-economics/taxdata


