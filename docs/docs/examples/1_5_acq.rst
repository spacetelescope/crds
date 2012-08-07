Target Acquisition
==================

COS Target Acquisition
----------------------

The COS acquisition exposure time calculators are used to help observers
determine the exposure times required for the different kinds of target
acquisition. There are four acquisition modes that can be used with COS:
ACQ/IMAGE, ACQ/SEARCH, ACQ/PEAKXD, and ACQ/PEAKD. These are described in detail
in |Chapter 8|_ of the COS IHB. Note that the acquisition ETCs do not include
overhead times associated with slews, grating changes, etc. These must be
determined separately by the user from the information provided in Chapter 9 of
the IHB or, in Phase II, with APT.

.. |Chapter 8| replace:: Chapter 8
.. _Chapter 8: http://www.stsci.edu/hst/cos/documents/handbooks/current/ch08.Acquisitions1.html

The target acquisition ETCs are very similar to the normal imaging and spectroscopic
ETCs, but there are some differences, as described below. Note that in all
cases, a S/N of 40 is recommended for all COS acquisition exposures, except exposures
that use the BOA for imaging target acquisitions. In this case a S/N of 60 is recommended.



Imaging Target Acquisition
~~~~~~~~~~~~~~~~~~~~~~~~~~


This ETC simulates the ACQ/IMAGE acquisition mode, and is almost identical to the imaging ETC. The only difference is the size
of the subarray used when calculating the signal to noise ratio (SNR). In the
normal imaging ETC the S/N is computed in a 170x170 pixel subarray, but for
acquisitions the subarray size is 345x816 pixels. A larger subarray is used to
account for the slight wobble associated with the Optics Select Mechanisms. The
NUV detector dark background for this imaging acquisition subarray is
approximately 208 counts per second.


Spectroscopic Target Acquisition
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This ETC simulates the ACQ/SEARCH, ACQ/PEAKD, and ACQ/PEAKXD modes.
For the NUV, the user selects the appropriate mode and (for PeakXD only) stripe. 


ACQ/SEARCH
..........

This mode uses a spiral search to locate the target. It can be done in either
imaging or dispersed light modes, so the user selects the appropriate
acquisition ETC to calculate exposure times. If done in dispersed light mode,
then the calculation is the same as for ACQ/PEAKD.

ACQ/PEAKXD and ACQ/PEAKD
........................

These dispersed light acquisition ETCs are very similar to the normal
spectroscopic ETCs, with two important exceptions.

First, the geocoronal airglow lines reduce the SNR for acquisitions because they
fill the aperture regardless of the pointing direction. To minimize this effect,
the spectral region around the two strongest geocoronal lines, 
:math:`Ly \alpha  \:\: \lambda_{0} = 1215.7` and :math:`O\: I\: \lambda_{0} = 1302`, 
are removed before the counts are summed by the flight software. Both of these
lines appear in the FUV.  The excluded region must be wide enough to account for
the full width of the entrance aperture, 2.5 arcsec, with a little extra margin.
The excluded region is approximately 350 pixels for G130M and G160M, and 1027
pixels for G140L.

The two remaining geocoronal lines, :math:`O\: I\: \lambda_{0} = 1356` and
:math:`O\: II\: \lambda_{0} = 2471` are both weak enough that no exclusion is
done. Since the latter line is the only geocoronal line in the NUV, no lines are
excluded for NUV dispersed light target acquisition.

The second difference is the number of stripes used for the NUV modes.  For
ACQ/PEAKD and ACQ/SEARCH it is most beneficial to use the light from all three
stripes, and the ETC computes the SNR on this basis. For ACQ/PEAKXD  one wants
to accurately locate the spectrum in the cross-dispersion direction, and the
position of a single stripe is measured.  The default stripe is B, but the user
may select either stripe A or C instead, if there is significantly more light in
one of these. For the FUV, no such complications exist. Counts from segments A
and B are added together, except for the excised geocoronal lines, to determine
the SNR.



STIS Target Acquisition
-----------------------

The STIS ACQ ETC allows calculations to be done for STIS ACQ observations and 
for imaging mode STIS ACQ/PEAK observations. (Results for spectroscopic ACQ/PEAK
observations must be estimated using the ordinary STIS spectroscopic ETC with 
CCDGAIN=4, CR-SPLIT=1, and 1x1 binning). 

STIS ACQ and ACQ/PEAK observations always
use the STIS CCD with CCDGAIN=4. The user must select either a STIS CCD imaging aperture
in order to calculate an ACQ observation, or a narrow STIS slit to calculate an 
ACQ/PEAK observation. 

For ACQ observations of extended targets, the user may also specify
the checkbox size over which the S/N is calculated. For extended source acquisitions,the 
user sets CHECKBOX=n, where n must be an odd number between 3 and 105: the checkbox will
then have dimension n x n pixels. CHECKBOX should be set to the minimum size which 
ensures that the brightest checkbox will be the one centered on the region of interest
(i.e., if your object is peaked within a region of 1 arcsecond, set 
CHECKBOX=21 [= (1 arcsecond) / (0.05 arcsecond/pixel) + 1]. The maximum checkbox is 105 
pixels on a side, or ~5 x 5 arcseconds. The subarray used for a diffuse-source acquisition
target image is CHECKBOX+101 pixels on a side. 


The ETC allows either point sources or extended sources to be
specified. If you are performing an extended source acquisition and know the
total brightness of the target, it may be useful to enter the desired checkbox size but
still specify a point source target, while if you know the surface brightness and approximate
angular diameter of the target it may be entered as an extended source. However, remember that
the ETC only calculates the S/N found when the specified source is centered in the check-box.
It does not perform any check of whether the selected check-box size is appropriate for the
source geometry.  For that purpose it is necessary to use the the STIS Target Acquisition
Simulator which can be found at http://www.stsci.edu/ftp/instrument_news/STIS/TAS/stis_tas.html

Other parameters in the STIS Acquisition ETC
are specified in the same way as standard imaging observations, except that there are no
additional CCD parameters.   
