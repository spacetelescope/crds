.. _extraction-region:

Extraction Regions
------------------

In older ETCs, the group of pixels over which the signal to noise ratio was
calculated was referred to as the "photometric aperture". We found that the use
of the word "aperture" sometimes caused confusion with instrument apertures, such
as slits or the location on the detector, so in the ETC, we have adopted the
term "extraction region".

When using imaging with point sources, the ETC will calculate the fraction of
the total flux that is contained within the user selected extraction region
using tables that are functions of size and the *effective wavelength*. For
extended sources, counts are calculated by *pysynphot* per square arc second and
are then converted to per pixel and multiplied by the number of pixels. When
performing spectroscopy, the fraction of counts at a particular wavelength is
calculated for some rectangular area (usually 1 resolution element wide) using 
tables indexed by the actual wavelength and region size.


For point sources, the present ETC offers the possibility to select among a wide
variety of extraction regions. The user should take into account that increasing
the extraction region size implies an increase in the detector and sky
noise/background. In general, in a noise limited regime, the extraction region
should be small. For bright object observations, for which Poissonian noise from
the source dominates, the extraction regions should be large to include most of
the source's flux.

The default extraction region selected by the instrument team (see table 1)
should be fine for most observations.

=========== ============================ ======================== ============= ==============
Instrument  Imaging                      \                        Spectroscopy  \
----------- ---------------------------- ------------------------ ------------- --------------
\           Point                        Extended                 Point         Extended
=========== ============================ ======================== ============= ==============
ACS/HRC     80% circle [2]_              2 pixel by 2 pixel box   9x2 box       2x2 box         
ACS/SBC     80% circle                   2x2 box                  15x2 box      2x2 box         
ACS/WFC     80% circle                   2x2 box                  5x2 box       2x2 box
COS/NUV     0.4 arcsec circle [1]_       0.4 arcsec circle        8x3 box       8x3 box
COS/FUV     0.4 arcsec circle            0.4 arcsec circle        47x6 box      47x6 box
STIS/CCD    80% circle                   2x2 box                  7x2 box       2x2 box    
STIS/NUV    80% circle                   2x2 box                  7x2 box       2x2 box    
STIS/FUV    80% circle                   2x2 box                  7x2 box       2x2 box
WFC3/IR     0.4 arcsec circle            5x5 box                  3x1 box       3x1 box
WFC3/UVIS   0.2 arcsec circle            5x5 box                  5x1 box       5x1 box
=========== ============================ ======================== ============= ==============


**Table 1: Default Extraction Regions**

The full set of extraction region tables are given in Appendix B.

.. [1] Radius
.. [2] A circle of sufficient size to enclose 80% of the light from the source.

