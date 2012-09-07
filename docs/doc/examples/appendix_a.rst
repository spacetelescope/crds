Appendix A - *pysynphot*
========================

PYSYNPHOT Calls
---------------

Table 5 lists the required *pysynphot* Calls for various types of ETC requests.

**Table 5 Required SYNPHOT Calls**

==========================================     =================================     ========================     ==================     ====================     
\                                              Imaging count rate                    Spectroscopic count rate     Thermal count rate     Effective Wavelength     
==========================================     =================================     ========================     ==================     ====================     
NICMOS and WFC3/IR Imaging                     Source and sky                        \                            Yes                    Yes                      
NICMOS and WFC3/IR (Slitless) Spectroscopy     Sky                                   Source                       Yes                    Yes                      
COS Imaging                                    Source and sky                        No                           No                     Yes                      
COS Spectroscopy                               No                                    Source [1]_ and Sky [2]_     No                     No                       
Other Imaging                                  Source and sky                        No                           No                     Yes                      
Other Slitless Spectroscopy                    Sky                                   Source                       No                     No                       
Slitted Spectroscopy                           No                                    Source [3]_ and sky [4]_     No                     No                       
Imaging with coronagraphy                      Field source, central source, sky     No                           No                     Yes                      
==========================================     =================================     ========================     ==================     ====================     

\

.. [1] Extended sources: The source is assumed to fill the aperture. A pixel-wise convolution is applied over the width of the aperture (2.5 arcsec). For purposes of the convolution only, a simplifying assumption is employed - the aperture is assumed to be rectangular. The values for various total counts are corrected for the actual shape.

.. [2] Sky background: A pixel-wise convolution is applied over the width of the aperture (2.5 arcsec). For purposes of the convolution only, a simplifying assumption is employed - the aperture is assumed to be rectangular. The values for various total counts are corrected for the actual shape.

.. [3] If the source is extended, a pixel-wise convolution is applied over the larger of the target width and the slit width (in pixels).

.. [4] A pixel wise convolution is applied over the slit width in pixels.

Pysynphot Call Descriptions
---------------------------

Imaging countrate
.................

The *pysynphot* "countrate" task has three required parameters: spectrum to 
calculate, magnitude and passband of spectrum, and science instrument. The information for the 
"magnitude and passband of spectrum" can be (and currently is) specified as part of the 
"spectrum to calculate" parameter. The other parameter is the "Science 
instrument" which is one of the three parts of the observation mode or 
"obsmode".

Spectroscopic countrate
.......................

When using the *pysynphot* countrate task and specifying an observation mode that includes a 
disperser (grating, grism or prism), there is an additional parameter "output". 
*pysynphot* will write the countrates, by :math:`\lambda-pixel`, to the specified file. Conveniently, 
countrate still returns to total count rate from the source, which is needed for calculating the 
global count rates for MAMA detectors.

For extended sources and the sky background, these count rates must then be convolved over the 
width of the aperture (or the width of the target if smaller). In slitless spectroscopy, we use the
conservative simplifying assumption that the background is evenly distributed over the entire 
detector. The alternative would require knowing the exact placement of the target source within the 
aperture.

Thermal countrate
.................

The contribution from the thermal background in NICMOS and WFC3 observations is calculated by the 
"thermback" task in *pysynphot* Thermback has only one required parameter, the '
"obsmode".

An example would look like::

  thermback.obsmode = ''nicmos,3,f110w''

Effective wavelength
....................

The effective wavelength of an observation is the centroid of the observation in lambda. That is 
to say, it is the weighted average wavelength of the curve which is the product of the target 
spectrum and the instrument throughput. The effective wavelength is used in the ETC for any 
calculation involving a wavelength dependant function such as the fraction of light in a circle of a 
given radius (for point sources).

The effective wavelength is calculated by the "calcphot" task which has three 
required parameters: obsmode, spectrum and form. The form is always flam.

An example would look like::

  calcphot.obsmode = ''acs,hrc,coron,f435w''
  calcphot.spectrum = ''rn(icat(k93models,3050,0.0,5.0),band(v),20.5,vegamag)''
  calcphot.form = ''flam''

The output from this example is::

  WARNING Spectrum not bounded. Using nearest neighbor: cat
  Mode = band(acs,hrc,coron,f435w)
    Pivot Equiv Gaussian
  Wavelength FWHM
    4310.291 728.5316 band(acs,hrc,coron,f435w)
  WARNING Spectrum not bounded. Using nearest neighbor: cat
  Spectrum: rn(icat((k93models,3050,0.0,5.0),band(v),20.5,vegamag)
    VZERO EFFLAM Mode: band(acs,hrc,coron,f435w)
  0. 4479.662

Pysynphot access
................

The cos_etccalc has been provided in STSDAS 3.8 (under PyRAF only) to provide COS ETC users with
access to the pysynphot results used by the COS ETC. For convenience, this task is part of the 
synphot package.

cos_etccalc requires two parameters, the obsmode and the spectrum, and accepts an optional output 
parameter. It returns all quantities used by the ETC: the pivot wavelength, the effective wavelength, 
and the total countrate (in counts per second); if a filename is provided in the output parameter, 
it will write the output spectrum (in counts per second), which is also used by the ETC, to that 
file. For example::

  cos_etccalc cos,nuv,g185m,c1986 ''rn(bb(15000),band(v),18.6,vegamag)''
  Obsmode: cos,nuv,g185m,c1986
  Spectrum: rn(bb(15000),band(v),18.6,vegamag)
  Pivot       Effective   Total
  Wavelength  Wavelength  COUNTRATE (counts/sec)
  1976.985602 1978.638255 4.713177

**Important note regarding renormalization in GALEX bandpasses**:

The GALEX magnitudes are provided in the AB magnitude system; however, pysynphot presently 
supports only magnitudes in the Vega system. Therefore, the ETC converts from ABmag to vegamag, 
using a constant offset correction, when constructing the pysynphot call. Users who wish to 
renormalize in a GALEX bandpass using the COS_etccalc task must apply the same correction.

The correction values are::

  vegamag = ABmag(GALEX_FUV) - 2.128
  vegamag = ABmag(GALEX_NUV) - 1.662

Further documentation can be obtained from the help file for the task. (help cos_etccalc)

Pysynphot Call Parameters
-------------------------

Observation Mode
................

The observation mode, or "obsmode" parameter is actually three separate parameters in 
many *pysynphot* tasks (instrument, detector and spec_el). Though the values can be specified 
separately, the ETC typically specifies the entire obsmode in the instrument parameter and leaves 
the other two blank. Thermback and calcphot both have a single obsmode parameter.


.. spectra should really be at ---- level,  but ..... not in TOC

Spectra
.......

CDBS contains a wide variety of input spectrum files. These are used by SYNPHOT and 
*pysynphot* for their calculations. Currently *pysynphot* only supports the functionality 
needed by the ETC; however, SYNPHOT is still provide a number of functions for generating synthetic
spectra and for manipulating spectra. SYNPHOT's capabilities are much more powerful and diverse than 
is needed for most observers. In general terms, the ETC uses only one continuum and/or up to three 
emission lines. An input file or synthetic spectra may be red shifted, reddened and/or renormalized.

Kurucz Models
.............

One of the catalogs of spectra described in Appendix B of the SYNPHOT User's Guide is the 
Kurucz Model Atmospheres. The ETC maps the spectral types to a set of parameters for a 
*pysynphot* "icat" function call. The parameters for the icat call for the Kurucz 
models are: catalog name (k93models), effective temperature, metallicity and log surface gravity. 
For example, the expression for a F2V star would be **icat(k93models,6890.0, 0.0,4.3)**.

Table 6 provides with a list of the available Kurucz models and the corresponding stellar 
parameters for these modes.

Table 6: *pysynphot* Parameters for Kurucz Model Stars

=============     =====     =====     =====     
Spectrum_Type     Teff      [M/H]     Log_G     
=============     =====     =====     =====     
O5V               44500     0.0       5.0       
O7V               38000     0.0       4.5       
O9V               33000     0.0       4.0       
B0V               30000     0.0       4.0       
B1V               25400     0.0       3.9       
B3V               18700     0.0       3.9       
B5V               15400     0.0       3.9       
B8V               11900     0.0       4.0       
A1V               9230      0.0       4.1       
A3V               8720      0.0       4.2       
A5V               8200      0.0       4.3       
F0V               7200      0.0       4.3       
F2V               6890      0.0       4.3       
F5V               6440      0.0       4.3       
F8V               6200      0.0       4.4       
G2V               5860      0.0       4.4       
G5V               5700      0.0       4.5       
G8V               5570      0.0       4.5       
K0V               5250      0.0       4.5       
K4V               4560      0.0       4.5       
K7V               4060      0.0       4.5       
M2V               3500      0.0       4.6       
G5I               4850      0.0       1.1       
M2I               3450      0.0       0.0       
F0I               7700      0.0       1.7       
=============     =====     =====     =====     


Bruzual Synthetic Stellar Spectra
.................................

These spectra are stored in CDBS and the correct file names can be determined
from table B4 in the SYNPHOT User's Guide.

HST Standard Star Spectra
.........................

These spectra are stored in CDBS and listed in the SYNPHOT User's Guide in Table
B3. The tricky part about using these spectra is to identify to identify the
best spectra to use. In some cases the spectra is updated with new data or
models and these are kept under separate versions. If a new classification is
made for the same star, the version number stats with "001". Each time a
particular version is update, this value is incremented by one. The best way to
identify which is the most up-to-date and best version  of the spectra to use is
to look in the CDBS web pages. In here the complete list of the HST calibration
spectra can be found under the `Throughput Tables (CALSPEC) <http://www.stsci.edu/hst/observatory/cdbs/calspec>`_ link. In this table the
recommended spectra, usually the one with the best resolution and broadest
wavelength range is listed first, at the left most column.

Non-Stellar Objects
...................

At the time that this document is being written, all of the spectra in this
category are stored in the home directory of the ETC itself. Please contact the
ETC development team for copies of these files.

Synthetic Spectra
.................

Black body spectra are implemented using the *pysynphot* function "bb" which
takes one parameter, the temperature of the object. For example "bb(5500)".

Power law spectra are implemented using the *pysynphot* function "pl" with
Jansky units, a reference wavelength of 4000 Angstroms and some user specified
exponent. The standard exponent used is -1 which would have an expression
of "pl(4000,-1,jy)".

A flat spectrum is a spectrum with constant energy per either wavelength unit or
per frequency unit. Flat spectra are implemented using the *pysynphot* function
"unit" with a value of 1 and either fnu or flam for the form. Note that
countrate calculations are done using **photons per wavelength unit**, as a
result, the plots of both forms are not actually flat when used in a count rate
calculation.

Emission lines
..............

Up to three emission lines can be superimposed on the input spectrum by the ETC.
For a pure emission line spectrum, use the "No continumm" option. Emission lines
are specified to the "countrate" task in *pysynphot* as part of the "spectrum"
task parameter.

An example would look like this (:math:`H\alpha` and [NII] lines with no continuum)::

  countrate.spectrum=''(em(6563.0,1.1,3.05E-14,flam)+em(6583.0,0.6,2.85E-15,flam)+em(6548.0,0.6,1.05E-15,flam))''

Sky spectra
...........

Count rates from the sky background are calculated by the same "countrate"
*pysynphot* task used to compute the source counts, the sole difference is in
the spectrum expression used in the calculation.

The sky background is derived from two master files that contain the
contributions from Earth shine and zodiacal light. The Earth shine contribution
is normalized via a multiplicative scale factor, while the zodiacal light
contribution is normalized by a surface magnitude specified in Vega magnitudes
per square arcsec in the Johnson V band.

Geo-coronal lines are added separately using the "em" function as described in
Emission lines, above.

An example would look like this::

 countrate.spectrum=''((earthshine.fits*0.5)+rn(spec(Zodi.fits),band(V),22.7,vegamag))''

