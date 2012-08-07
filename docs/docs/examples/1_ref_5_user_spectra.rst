.. _user-supplied-spectrum:

User-Supplied Spectra
---------------------

One of the features of the ETC is its ability handle a spectrum supplied by the user. In this 
version of the ETC this is accomplished by a direct upload from the machine where the user is 
running the web browser.

To use this option, you will need to:

- Prepare your spectrum file
- Specify your spectrum file in the ETC input form

The file will be uploaded when you click the "submit" button at the top or bottom of 
the form. If the file is large or the computer has a slow internet connection it will take extra 
time for the browser to send the file to the ETC server.

Prepare your file
.................

Prepare your input spectrum file with 2 columns:

- column 1: wavelength
- column 2: flux density

Column 1 should be the wavelength in :math:`\AA` and column 2 should be the flux density (in 
:math:`erg \cdot cm^{-2} \cdot sec^{-1} \cdot \AA^{-1}` for point sources, and in 
:math:`erg \cdot cm^{-2} \cdot sec^{-1} \cdot \AA^{-1} \cdot arcsec^{-2}` for diffuse sources). 
The wavelengths in the first column *must* be in increasing order. Please note that if your 
spectrum has zero or negative wavelength or flux values anywhere in the file, you will get a 
*pysynphot* error message.

The user specified spectrum file should be in one of the following 2 file formats:

- ASCII table with the extension `.dat`
- FITS table with an extension `.fits` or `.fit`

Try to use a unique filename for this file, for example by using your last name as part of the filename.

Spectrum File Format
....................

ASCII
+++++

If the file is an ASCII file, it must contain the following 2 columns:

- column 1: wavelength (in :math:`\AA`)
- column 2: flux density in :math:`erg \cdot cm^{-2} \cdot sec^{-1} \cdot \AA^{-1}` for point sources, 
    in :math:`erg \cdot cm^{-2} \cdot sec^{-1} \cdot \AA^{-1} \cdot arcsec^{-2}` for diffuse sources

Any comment lines in the file must start with # in order to avoid confusion when it 
is used in the calculation.

SDAS
++++

**The SDAS table file format is not portable to different machine architectures and so support 
for it has been discontinued. We recommend using the TTools command "tcopy" to convert 
all SDAS files to FITS format.**

FITS
++++

If the file is a FITS binary table, it should have two columns labeled "WAVELENGTH" and 
"FLUX", again with the units specified for each column. The header of the FITS table 
should then include lines similar to these::

 PCOUNT = 0 /
 GCOUNT = 1 / Only one group
 TFIELDS = 2 / Number of fields per row
 EXTNAME = 'f4v_v15_flam.tab' / Name of extension
 TTYPE1 = 'WAVELENGTH' /
 TBCOL1 = 1 /
 TFORM1 = 'E15.7 ' /
 TUNIT1 = 'angstroms' /
 TDISP1 = 'G15.7 ' / %15.7g
 TTYPE2 = 'FLUX ' /
 TBCOL2 = 17 /
 TFORM2 = 'E15.7 ' /
 TUNIT2 = 'flam ' /
 TDISP2 = 'G15.7 ' / %15.7g

Specify your spectrum
.....................

In section 3 of the ETC input form, simply check the box next to "User Supplied Spectrum". 
You may then either type the path of the file in the input box, or use the 
"browse" button next to the box and then navigate through the local file system to the 
file.

.. image:: images/fr.3.1_user_spectrum.gif
   :scale: 100 %
   :alt: Graphic1

