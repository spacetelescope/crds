COS Tables
----------

Detector Count Rate Restrictions
................................
\

The ETC uses the current count rate screening restrictions, which are taken from Section 11.5 of 
the COS Instrument Handbook. If the observation will exceed any of the count rate restrictions, a 
warning message will be given in the output page. The count rate restrictions for the detectors are 
as follows:

COS Count Rate Screening Limits
...............................
\
  
============ ==================== ================= ============================== 
**Detector** **Source type** [1]_ **Type_of_limit** **Limiting count rate** [2]_   
============ ==================== ================= ============================== 
FUV          Predictable          Global            15,000 per segment             
FUV          Predictable          Local             0.666 per pixel ??? 40 per resel        
FUV          Irregular            Global            6,000 per segment              
FUV          Irregular            Local             0.666 per pixel ??? 40 per resel [3]_              
NUV          Predictable          Global            30,000 per stripe              
NUV          Predictable          Local             70 per pixel                   
NUV          Irregular            Global            12,000 per stripe              
NUV          Irregular            Local             70 per pixel                   
NUV          Imaging              Global            170,000 (over entire detector) 
NUV          Imaging              Local             50 per pixel                   
============ ==================== ================= ============================== 

\

.. [1] "Predictable" means the brightness of the source can be reliably 
   predicted for the time of observation to within 0.5 magnitude.

.. [2] Entries are counts per second.

.. [3] The FUV spectral resolution is 6 pixels, the NUV is 3 pixels.

Detector Dark Background
........................
\

The following table lists the dark count rate and read noise characteristics of
the COS detectors as measured in ground tests.

Detector background count rates (per second) for COS
....................................................
\

================================= ================================================================================ =============================================================================== 
**Detector:**                     **FUV_XDL**                                                                      **NUV_MAMA**                                                                    
================================= ================================================================================ =============================================================================== 
Dark rate (counts sec\ :sup:`-1`) ??  per cm\ :sup:`2`                                                             11 per cm\ :sup:`2` 
\                                 2.25 x 10\ :sup:`-6` per pixel                                                   6.875 x 10\ :sup:`-5` per pixel
\                                 1.35 x 10\ :sup:`-5` per resel                                                   2.0625 x 10\ :sup:`-4` per resel
Read noise                        0                                                                                0                                                                               
================================= ================================================================================ =============================================================================== 
