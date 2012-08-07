STIS Modes
-----------

Selecting a Slit/Filter
.......................

All of the supported slits for this Cycle are available on the ETCs. The pull-
down menu gives the supported slits and filters for the chosen grating/prism.
Since the filters and the slits are in the same wheel, you can choose either a
slit or a filter. In case of the neutral density filters, the pull-down menu
gives the density of the filter in "log10" units, i.e. ND=1 corresponds to an
attenuation factor of 10, ND=2 corresponds to an attenuation factor of 100, etc.
In the case of  the slits, the pull-down menu gives the slit height and slit
width in arcsec. To choose the best slit width, you may need to know the number
of detector pixels corresponding to the slit-width. The table below gives the
plate scales for different gratings.

Plate Scales for Different Gratings
...................................
\
 
=============== ==================== ============== 
 **Grating**    **Plate_Scale_(arcsec/pixel)**
--------------- -----------------------------------
\               **Along_Dispersion** **Along_Slit** 
=============== ==================== ============== 
First Order CCD 0.05                 0.05           
G140L, G230L    0.0244               0.0244         
G140M, G230M    0.0290               0.0290          
E230M           0.0290               0.0290          
E140M           0.0290               0.0290          
E230H           0.0290               0.0290          
E140H           0.0290               0.0290         
=============== ==================== ============== 

Detector Countrate Restriction
..............................

The ETC uses the current MAMA countrate restrictions, which are taken from the
*STIS Instrument Handbook*. If the observation will exceed any of the countrate
restrictions, a warning message will be given in the output page. This is
particularly useful to check if the observations will exceed the bright-object
protection (BOP) limit of the MAMA detector. The countrate restrictions for the
detectors are as follows:

CCD Saturation Limits
.....................
\
  
======== ==================== ========= =============== ============ 
**Gain** **Saturation Level** \         **Full Well**   \            
-------- ------------------------------ ----------------------------
\        **(electrons)**      **(ADU)** **(electrons)** **(ADU)**    
======== ==================== ========= =============== ============ 
1        33,000               30,000    120,000 [1]_    120,000 [1]_ 
4        144,000 [1]_         30,000    120,000 [1]_    30,000       
======== ==================== ========= =============== ============ 

\

.. [1] The fullwell limit for gain=4 is 144,000 near the center of the chip and
   only 120,000 near the edges.

MAMA Countrate Restrictions for Different Modes
...............................................
\

============ ==================== ====================== =============================== =================== ================== 
**Detector** **Target**           **Local Limit**        **Global Limit**                                                     
------------ -------------------- ---------------------- ----------------------------------------------------------------------
\                                                        **(First-order + Prism Modes)** **(Echelle Modes)** **(Imaging Mode)** 
-------------------------------------------------------- ------------------------------- ------------------- ------------------
\                                 **(counts/sec/pixel)** **(counts/sec)**                **(counts/sec)**    **(counts/sec)**   
================================= ====================== =============================== =================== ================== 
NUV-MAMA     Non-variable         100                    30,000                          200,000             200,000            
FUV-MAMA     Non-variable         75                     30,000                          200,000             \                  
NUV-MAMA     Irregularly Variable 75                     12,000                          80,000              \                  
FUV-MAMA     Irregularly Variable 75                     12,000                          80,000              \                  
============ ==================== ====================== =============================== =================== ================== 


In the case of the echelle modes, there is some extra noise because of the
scattered light which runs across the orders. The updated version of the ETC
takes this extra noise into account (to a first approximation) in the
calculation of the S/N ratio. The global countrate estimates take the scattering
into account.

For imaging mode the peak countrates mentioned in the output need some
explanation. The peak countrates are used *only* to check for the MAMA bright
object protection issues. Since the health of the detector sometimes relies on
our ability to predict the peak countrate in a given observation, we have been a
bit conservative in our estimates of peak countrates, particularly for the
MAMAs. At present, the calculation of peak count rates for the point sources
assume that the encircled energy in the central pixel is 30% in case of the CCD,
and 25% in case of the MAMAs. This can be sometimes over conservative and can be
slightly larger than a factor of 2 for some MAMA modes. A more accurate
algorithm will be added in the future, which will take the spectral shape of a
given source and the filter combination into account to calculate the
appropriate percentage of enclosed energy in the central pixel.

Detector Binning
................

The CCD has 3 binning factors: x1, x2 and x4. In Imaging mode the binning
factors must be the same in each detector dimension, but for spectroscopy the
factors can be different. Since the readnoise of the CCD applies only to a
'binned' pixel, using a binning factor greater than one can reduce the overall
noise in some cases. However, this comes at the price of degraded spatial (or
spectral) resolution. The readnoise and saturation characteristics of the CCD
are given in the Table below. (Note that the MAMA detectors have no readnoise,
so the binning option is ignored in these cases.)

Detector Background
...................

STIS ACQ and ACQ/PEAK observations are always done using an unbinned subarray
and a CCD gain setting of 4. For these parameters, the expected dark current is
about 0.009 e-/s, and the expected read noise is about 7.75 e-.

============ ================================== ============== 
**Detector** **Dark**                           **Read_Noise** 
============ ================================== ============== 
CCD (Gain=1) 0.0161 electron/pixel/s             5.6_e-         
CCD (Gain=4) 0.0161 electron/pixel/s             8.3_e-         
NUV-MAMA     3.5 * 10\ :sup:`-3` count/pixel/s  0.             
FUV-MAMA     1.50 * 10\ :sup:`-4` count/pixel/s 0.             
============ ================================== ============== 

Setting the CCD gain to 4 is useful if you are expecting a large number of
counts. For faint sources, where the counts are expected to be lower, gain=1 may
be preferable since the readnoise in that case is lower.

To avoid an excessive number of cosmic ray detections with the CCD, longer
exposures should be split (CR-split) in order to:
 
- keep the number of detected cosmic rays low
- be able to remove the cosmic rays during data reduction

Using CR-split increases the effective readnoise, which is taken into account in
the exposure time calculations. The default CR-split is 2.

Selecting a Checkbox Size for STIS Target Acquisitions
......................................................

For extended source acquisitions, the user sets CHECKBOX=n, where n must be an
odd number between 3 and 105: the checkbox will then have dimension n x n
pixels. CHECKBOX should be set to the minimum size which ensures that the
brightest checkbox will be the one centered on the region of interest (i.e., if
your object is peaked within a region of 1 arcsecond, set CHECKBOX=21 [= (1
arcsecond) / (0.05 arcsecond pixel-1) + 1]. The maximum checkbox is 105 pixels
on a side, or ~5 x 5 arcseconds. The subarray used for a diffuse-source
acquisition target image is CHECKBOX+101 pixels on a side. The STIS Target
Acquisition Simulator can be used to determine the optimal CHECKBOX size.
