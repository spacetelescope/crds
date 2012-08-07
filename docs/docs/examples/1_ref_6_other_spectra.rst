.. _other-hst-spectrum:

Other HST Spectra
-----------------

There are a large number of spectrum files available for use in Calibration Database System 
(CDBS). Some of these are discussed in the 
`SYNPHOT Data User's Guide <http://www.stsci.edu/hst/HST_overview/documents/synphot/hst_synphot_cover.html>`_. Any file in CDBS can 
be used if the user is able to determine a valid path name for the file.

For example, the Bruzual Synthetic Spectral Atlas (table B4) can be found in the CDBS directory 
"crgridbz77$", so to specify the F2V file from this atlas. Use filename 
"crgridbz77$bz_19.fits" in the ETC user input form as shown below.

HST Standard Spectra (CALSPEC and CALOBS)
.........................................

CALSPEC contains the composite stellar spectra that are the fundamental flux standards for HST 
calibrations. All files are in machine independent binary FITS table format. Information about the 
pedigree of a given spectrum is in the header of the FITS table file. Further details about these 
files as well as access to these files can be found at 
`the CALSPEC webpage <http://www.stsci.edu/hst/observatory/cdbs/calspec.html>`_

CALOBS contains several versions of the ultraviolet (UV) and optical spectra of the fundamental 
flux standards used for HST calibrations. Some of these files contain the original data obtained 
from different sources (UV: VOYAGER2 or IUE; optical: Oke, Tapia or Stone; or STIS), while others 
contain corrected or updated versions. Updates to the flux distributions are indicated by file names 
with the same root name but incremental version number. The earlier versions are retained for 
comparison purposes. All files are in machine independent binary FITS table format. Information 
about the pedigree of a given spectrum is in the header of the FITS file. Further details as well as 
these files can be found at `The CALOBS webpage <http://www.stsci.edu/hst/observatory/cdbs/calobs.html>`_

How to provide "Other HST Spectrum" to the ETC
..............................................

To use one of the CDBS supplied spectrum file, select the "Other HST Spectrum" option in section 
3 of the ETC input form and type the file path in the text box as shown below:

.. image:: images/f1.ref.6_other_spectra.gif
   :scale: 100 %
   :alt: Graphic1

