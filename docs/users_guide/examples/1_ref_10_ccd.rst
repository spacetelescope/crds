.. _ccd-parameters:


CCD parameters
--------------

ACS CCD Parameters
..................

The new ACS CCD electronics installed in SM4 permit four A/D gain
settings for the Wide Field Channel: nominally 0.5, 1.0, 1.4, and 2.0
e-/DN. All are available to the observer, but only gain 2.0 is
presently supported by STScI with calibration reference files. The
default gain is 2.0 e-/DN, which critically samples the read noise and
spans the full pixel well depth of ~84000 e-. Consult the ACS
Instrument Handbook for the precisely measured value of each gain
setting.

The High Resolution Channel of ACS was not recovered during SM4, so it
remains unavailable for any science or calibration uses.

The user can specify the number of distinct frames (exposures)
composing an observation to mitigate the deleterious effects of
cosmic-ray hits and bad pixels. Cosmic-ray hits in long exposures can
be remedied with the "CR-SPLIT" parameter, which allows (1) fewer
numbers of detected cosmic rays per exposure, and (2) the
identification and removal of cosmic-rays during data
reduction. Dithering is recommended over the use of CR-SPLIT because
dithering mitigates the effects of both cosmic-ray hits and bad pixels
and enables greater sampling of the point-spread function. The user
should beware that the ETC uses a default setting of CR-SPLIT=2,
whereas the default setting for Phase 2 proposal preparation with APT
is CR-SPLIT=NO.

To avoid an excessive number of cosmic ray detections with the CCD,
longer exposures should be split (CR-split) in order to:

1. keep the number of detected cosmic rays low
2. be able to remove the cosmic rays during data reduction

The default CR-split is 2.

Quantum Yield correction for CCD detection of UV photons
........................................................

For CCD detectors in the optical, each detected photon usually
generates a single electron (i.e., photons absorbed × the gain
correspond to the total number of electrons). However, in the near UV,
shortward of ~3200 Å, there is a finite probability of creating more
than one electron per detected UV photon (see Christensen, O., 1976,
J. App. Phys., 47, 689). The throughput curves adopted in pysynphot
correctly predict the number of electrons generated per incident
photon and implicitly include this UV quantum yield
correction. However, since multiple electrons are generated from a
single photon, the actual number of photons detected, and therefore
the S/N obtained, is less than the number of electrons detected would
suggest.

To take this into account, the ETC corrects the number of electrons
calculated by pysynphot by dividing the results of the pysynphot
calculation by Q, the mean number of electrons generated per
photon. For imaging mode calculations, this correction is calculated
by applying the correction appropriate for photons at a wavelength
equal to the "effective wavelength" determined for the pysynphot
calculation. For spectroscopic CCD observations, Q is calculated
correctly for each wavelength bin. The "source count" rate reported by
the ETC for CCD observations is actually this corrected count rate
rather than the true number of electrons predicted by
pysynphot. However, the true uncorrected number of electrons is used for
comparison with the CCD saturation limits and for the "Brightest Pixel
(single exposure)" quantities.

STIS CCD Parameters
...................


For the STIS CCD, the default gain value of 1 offers the lowest read
noise, but the analog-to-digital converter then limits the maximum
signal that can be detected without saturation to about 33,000 e- per
pixel. Using a CCDGAIN setting of 4 allows the full well of the CCD to
be used (about 144,0000 e- per pixel near the center of the CCD and
about 120,000 e- per pixel near the edges). The CCDGAIN=4 setting has
the disadvantage that an additional large scale pattern noise is
imposed on the image. It has the advantage that, the CCD response when
using CCDGAIN=4 remains linear even beyond the 144,000 e- full well
limit if one integrates over the pixels bled into, and for specialized
observations needing extremely high S/N, this property may be
useful.

The STIS CCD also allows pixels to be binned by factors 1, 2, or 4
during the readout. This will reduce the read noise at the expense of
spatial information. For spectroscopic observations, separate binning
factors can be specified for the spatial and dispersion
directions.

For the STIS CCD, CR-SPLIT=2 is the default.

STIS ACQ modes always use the CCD with CCDGAIN=4 CR-SPLIT=NONE and no
binning, so the STIS ACQ mode ETC does not include any user adjustable
additional CCD parameters.

For calculations using the STIS MAMA modes, the settings specified for
the additional CCD parameters are ignored.


WFC3 CCD Parameters
...................

**# Frames**

Here the user can specify the number of distinct frames (exposures) comprising their observation.

This is analogous to the "CR-SPLIT" parameter that was popular in the early days of 
HST, but today has been supplanted by distinct exposures taken in tandem with dithering, allowing 
not only the rejection of cosmic rays but also the masking of detector artifacts and a resampling of 
the point spread function.

*Note for WFC3 IR:* This item does not specify the number of non-destructive reads 
taken within a single exposure, but rather specifies the number of independent exposures (e.g. 
different dither pointings). The readnoise for each independent exposure ("frame") 
assumes the maximum allowed number of non-destructive readouts.

**Detector Chip**

The WFC3 detector consists of two halves, similar to the ACS/WFC. Chip 2 is more sensitive in the 
UV than chip 1.
