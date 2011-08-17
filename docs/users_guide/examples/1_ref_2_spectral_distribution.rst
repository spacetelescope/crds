.. _spectral-distributions:

Spectral Distributions
----------------------

Here you can either enter your own input spectrum for the source (details 
given in the next section), or you can choose one of the following:

Castelli & Kurucz Models
........................

This atlas contains about 4300 stellar atmosphere models for a wide
range of metallicities, effective temperatures and gravities.  These
LTE models with no convective overshooting computed by Fiorella
Castelli, have improved upon the opacities and abundances previously used
by Kurucz (1990). The main improvements, as detailed in Castelli and
Kurucz (2003), are the use of improved solar abundances and TiO lines.


A
complete set of files can be found `<http://www.stsci.edu/ftp/cdbs/grid/ck04models>`_
  

  
Pickles Models
..............

This library of wide spectral coverage consists of 131 flux
calibrated stellar spectra, encompassing all normal spectral types and
luminosity classes at solar abundance, and metal-weak and metal-rich
F-K dwarf and G-K giant components. Each spectrum in the library is a
combination of several sources overlapping in wavelength coverage. The
creator of the library has followed precise criteria to combine
sources and to assemble the most reliable spectra. As part of the
selection criteria prior to combination, all input sources were
checked against the SIMBAD database and against the colors and line
strengths as derived by the observed spectra themselves to make sure
they had similar spectral types (A.J. Pickles 1998, PASP 110, 863). A
complete set of files can be found at `<http://www.stsci.edu/ftp/cdbs/grid/pickles>`_


  
Kurucz Models
.............

There are 24 stellar spectra available. All are Kurucz models
calculated from the Kurucz database (Dr. R. Kurucz, CD-ROM No. 13,
GSFC), which have been installed in CDBS. These are the same spectra
used as input spectra by Leitherer, et. al. 1996, in ISR ACS 96-024,
*MAMA Bright Object Limits for Astronomical Objects.* See also
*The Solar Blind Channel Bright Object Limits for Astronomical
Objects* by Boffi & Bohlin 1999, ISR ACS 99-07. A complete set
of files can be found `<http://www.stsci.edu/ftp/cdbs/grid/k93models>`_

Bruzual Spectra
................

The Bruzual Atlas contains 77 stellar spectra frequently used in the synthesis 
of galaxy spectra. 

For more information, see the `relevant section <http://www.stsci.edu/hst/observatory/cdbs/astronomical_catalogs.html#bruzual>`_ of the CDBS webpage on `astronomical catalogs <http://www.stsci.edu/hst/observatory/cdbs/astronomical_catalogs.html>`_. A complete set of files can be found at `<http://www.stsci.edu/ftp/cdbs/grid/bz77>`_

HST Standard Star spectra
.........................

Several HST calibration standard spectra are available. These spectra
are stored in CDBS and were chosen from the paper *Spectrophotometric
Standards from the Far-UV to the Near-IR on the White Dwarf Flux
Scale* by Bohlin 1996, AJ, 111, 1743. See also *Comparison of White
Dwarf Models with ACS Spectrophotometry* by Bohlin 2000, AJ,
120, 437. The selection also includes a spectrum of the Sun. A
complete set of files can be found at `<http://www.stsci.edu/hst/observatory/cdbs/calspec.html>`_

  
Non-Stellar Objects
...................


There are also a few model spectra of non-stellar objects available
from CDBS, such as an elliptical galaxy, a Seyfert galaxy, the Orion
nebula, and a planetary nebula. These options are not all available
for all the instruments because their data do not cover the relevant
spectral range. A word of caution is necessary on the use of these
model spectra. These are only "typical" examples, and
individual cases may well have very different spectra. For example,
the PN spectrum is that of NGC 7009, but other PNe with different
excitation classes may have very different spectral
characteristics.
  
QSO
...

Two templates are offered with user-supplied redshift. The
QSO SDSS spectrum refers to a composite spectrum of a sample of QSOs,
transformed to z=0 (Francis et al. 1991, ApJ, 373, 465). Other QSOs
may have very different spectral characteristics and some caution is
advised in using these model spectra. The QSO spectrum at zero
redshift has a rather limited wavelength range (800 - 6000 A). As a
result, using high redshifts may put the QSO spectrum beyond the
wavelength region of the filter or grating bandpass, thereby causing
the ETC to return an error. Conversely, using a QSO with a very low
(or zero) redshift will result in a spectrum with no flux in the
infrared, which would cause the ETC to return an error when using
WFC3/IR. The QSO FOS-SVP composite spectrum has been smoothed above
2900A and below 700A. More details about the FOS spectra can be
obtained from `<http://archive.stsci.edu/prepds/composite_quasar/>`_
  
Black-body
..........
  
with a user specified temperature.


Power-law
.........

The flux distribution is given by 

:math:`F(\lambda) = \lambda^n`

where *n* is specified by the user. 
  
Flat continuum
..............

This is a special case of the power law, where n=0. This distribution
is so named because the spectrum has constant (flat line) energy per
either wavelength or frequency units. Please note that countrate
calculations use photons per wavelength unit.
