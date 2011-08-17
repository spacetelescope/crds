.. _specifying-background:

Specifying the Appropriate Background
-------------------------------------

There are several potential types of background and noise that can affect the
observations; the main contributors being:

#. Earth-shine
#. Zodiacal light
#. Geo-coronal emission Lines (UV)
#. Thermal background (IR)
#. Dark current
#. Read noise (CCDs and NICMOS)


External Background
-------------------

Earthshine can vary strongly depending on the Earth-target angle and the
fraction of the sun-lit earth. The contribution of zodiacal light does not vary
dramatically with time, and is constant within a factor of about 3 throughout
the sky available to HST. Thus, while the Earthshine can be kept low by a
careful choice of the epoch of observations, the zodiacal light can be the most
dominant contribution.

Earthshine and zodiacal light values are based on the prescriptions by Giavalisco
et al.   `WFC3 ISR 2002-012 <http://www.stsci.edu/instruments/wfc3/ISRs/WFC3-2002-12.pdf>`_

The geo-coronal emission is confined to mostly a very few lines such as Lyman-
alpha, which must be taken into account for UV observations.

The table below lists the contributions of the zodiacal light and Earthshine
corresponding to these levels.

**Table 1: Sky Background Contributions**

================     ============     =======     ====     =========     
Background           Contribution
----------------     -----------------------------------------------
\                    Low              Average     High     Very High     
================     ============     =======     ====     =========     
Zodiacal [a]_        23.3             22.7        22.1     NA            
Earth_shine [b]_     0                50          100      200 [c]_      
================     ============     =======     ====     =========     

.. [a] Vega magnitudes per square arc second in Johnson/V band.
.. [b] As a percentage of the "High" value.
.. [c] Corresponds to limb angle 24 degrees.



**Table 2: Geo-Coronal Emission Line Properties**

.. |A| replace:: Angstrom
    
.. |Flux| replace:: Flux(erg cm^-2 s^-1)

===========     ============== ==================     ========     ===================     ========    ====================   ========     
Line            \              Low                                 Average                             High                               
-----------     -------------- -------------------------------     --------------------------------    -------------------------------
\               Wavelength |A| |Flux|                 FWHM |A|     |Flux|                  FWHM |A|    |Flux|                 FWHM |A|     
===========     ============== ==================     ========     ===================     ========    ====================   ========    
Lyman_Alpha     1215.7         6.1e-14                0.04         3.05e-13                0.04        6.1e-13                0.04        
O_I             1302           3.8e-16                0.013        2.85e-14                0.013       5.7e-14                0.013       
O_I             1356           3.0e-17                0.013        2.5e-15                 0.013       5.0e-15                0.013       
O_II            2471           1.5e-17                0.023        1.5e-15                 0.023       3.0e-15                0.023       
===========     ============== ==================     ========     ===================     ========    ====================   ========

The strength of the geo-coronal Lyman alpha varies between about 2 and 20 kilo
Rayleighs, depending on the time of observations and the position of the target
relative to the Sun, and can be kept low by the special requirement
"SHADOW". For more details, see the *Instrument Handbook* and the
*HST Phase II Proposal Instructions*.

Thermal Background and Noise
----------------------------

The thermal background is negligible below about 8000 |A| and increases
slowly towards longer wavelengths. For WFC3/IR, the thermal count rate (per
unbinned pixel) is calculated by an algorithm that is
described in detail in "Thermal Background Limitations for IR Instrumentation Onboard HST", Sosey, M., Wheeler, T., Sivaramakrishnan, A.,
2003, `NICMOS ISR 2003-007 <http://www.stsci.edu/hst/nicmos/documents/isrs/isr_2003-007.pdf>`_

Detector dark current is an intrinsic source of background counts. The dark
current rate is dependent upon the detector design and temperature. It is
measured in counts per unbinned pixel per second.

CCD and CCD-like detectors (such as the WFC3 IR detector) are subject to
noise caused by the process of "reading out" the charge accumulated by the
pixels. The amount of read noise varies by detector and as a function of gain.
Read noise is measured per binned pixel, per read.

**Table 3: Dark Current and Read Noise Values**

==========     ==========================     ==================     
Instrument     Dark_Current                   Read_Noise
\              (counts sec^-1 pixel^-1)       (for gain = 1)         
==========     ==========================     ==================     
ACS/HRC        0.00372                        4.7 (for gain=2.0)     
ACS/SBC        0.000012                       NA                     
ACS/WFC        0.00622                        4.1                    
COS/FUV        2.25e-06                       NA                     
COS/NUV        7.4e-4                         NA                     
STIS/CCD       0.0161                         5.6                    
STIS/FUV       0.00015                        NA                     
STIS/NUV       0.0035                         NA  
WFC3/IR        0.0221                         14.6 (for gain=2.5)
WFC3/UVIS      0.0005                         3.0  (for gain=1.5)
==========     ==========================     ==================     



