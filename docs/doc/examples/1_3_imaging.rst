Imaging
=======

Imaging calculations use the effective wavelength of the observed spectrum to determine wavelength-dependent values such as the fraction of flux enclosed in a region.

In addition to the basic calculation results, for point sources, the imaging ETCs also estimate the fraction of flux enclosed in the specified extraction region, and the optimal SNR, described below.


Optimal SNR
-----------

**Calculating Optimal SNR (PSF-Fitting)**

The Optimal SNR is an estimate of the SNR when photometric information is
extracted using a PSF fitting algorithm. Another use of the Optimal SNR is to
allow direct quantitative comparison between instruments with different scales
(i.e. arc seconds per pixel). The formulas used in this calculation are based
upon Heyer & Biretta, 2005, WFPC2 Instrument Handbook, Version 9.1 (see also
Keith Horne, PASP, 1986, 98, 609). This formula uses the PSF sharpness, which is
effectively the reciprocal of the number of pixels contributing background
noise. For calculating the *sharpness*, we have considered the conservative case
in which the point source is centered in the corner of a pixel. Note that this
may be the cause of some apparent discrepancies when comparing with standard
SNR-t calculations for the brightest pixel (which assume the conservative case
of the object being centered on the pixel).


.. image:: images/f1.3.1osnr.gif
   :scale: 100 %
   :alt:    OSNR  = S_c / sqrt(S_c + (BG_c + RN^2) / Sharpness)

Where:
      | OSNR = Optimal Signal To Noise Ratio
      | S\ :sub:`c` = Total Source counts
      | RN = Read Noise
      | BG\ :sub:`c` = Background counts
      | Sharpness = sum of i,j (PSF(i,j)\ :sup:`2`)

.. image:: images/f1.3.2sc.gif
   :scale: 100 %
   :alt:    S_c = S_r * T


Where:

  | Sr = Source count rate
  | T = Exposure Time

.. image:: images/f1.3.3bg.gif
   :scale: 100 %
   :alt:   BG_c = Sky_c + DC_c + Thermal_c + CS_c
   

Where:

  | BG\ :sub:`c`  = Total Background counts/pixel
  | Sky\ :sub:`c` = Sky counts (Earth Shine + Zodiacal Light + Geocoronal Emission Lines)
  | DC\ :sub:`c`  = Dark Current counts
  | (Thermal\ :sub:`c`) = (Optional) Thermal Background counts
  | (CS\ :sub:`c`) = (Optional) Coronagraphic Source
