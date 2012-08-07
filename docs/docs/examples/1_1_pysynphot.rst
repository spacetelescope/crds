ETC and *pysynphot*
===================

The ETC relies heavily on the synthetic photometry package
*pysynphot*. This package simulates photometric data and spectra
as they are observed by the HST instruments.  For this, it relies on
the information about the HST instrument throughputs that are included
in the Calibration Data Base System (CDBS) at STScI. 

.. XXX Do we still need the discussion of transitioning?

XXX **<a href="transition_py_syn.html">Pysynphot</a>** is intended as a
modern-language successor to the IRAF/STSDAS SYNPHOT package, and is
developed and maintained by the Science Software Branch (SSB) at
STScI.

Except for the details of the SYNPHOT call descriptions and
parameters, the ETC documentation describing SYNPHOT applies equally
well to pysynphot.

The diagram below depicts the relationship between the ETC and
pysynphot. Each instance of the ETC contains its own pysynphot
implementation, but refers to an external CDBS collection for the
appropriate reference files. This allows the CDBS reference files to
be updated without changing the ETC codebase. The ETC handles the
conversion between the ETC request and the pysynphot request
internally.

.. image:: images/f1.1.0pysynphot.gif
   :alt: ETC/Pysynphot Relationship
   
