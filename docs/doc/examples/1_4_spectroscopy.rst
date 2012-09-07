Spectroscopy
============

Spectroscopic calculations compute the time or SNR at the specified observation wavelength.

In addition to the basic calculation results, the spectroscopic ETCs also present plots of the signal to noise as a function of wavelength, and the total counts from each component of the calculation.

Specifying the Wavelength
-------------------------

After selecting the central wavelength setting for the desired grating
in the instrument configuration section, the user must also, in the
next section, specify an observation wavelength that is within the
wavelength range for that configuration.  Information about the valid
wavelength ranges is available on the forms. If the specified
wavelength is not in the correct range, the calculation will not run
and the user will get an error message.

In previous ETCs,

  - the central wavelength setting was selected based
    upon the observation wavelength setting specified by the user. In this
    version, the user must select the central wavelength setting that they
    want to use. This allows the user to choose, in some cases, between
    two central wavelength settings that both cover the desired
    observation wavelength.

  - when a new grating or central wavelength value was
    selected, the wavelength specified for the S/N calculation was checked
    and, if outside the valid range, was automatically reset to the
    midpoint of the valid range for that grating/CENWAVE combination. 
    This automatic resetting is no longer performed.


Extended Sources
----------------

Increasing the slit width on a spatially extended source degrades the
resolution. This degraded resolution is:

:math:`D = (slit-width) / (m_{\lambda}) * (\delta-\lambda \: per \: pixel)`

where

:math:`m_{\lambda}` is the plate-scale in the dispersion direction.

In other words, the actual resolution is degraded by a factor R, the slit width
in pixels/2.  In the current ETC implementation, this degradation in resolution
is simulated by a convolution of the input spectrum over the slit width. Thus
cases that were handled only in an approximate way by older ETC versions (e.g.
input spectra with narrow lines, geocoronal lines in the STIS/FUV) are now
handled more correctly.

For slitless spectroscopy, the sky background is assumed to uniformly fill the
detector. In truth, the geocoronal lines don't uniformly fill the detector, but
attempting a more accurate simulation could run the risk of being too optimistic.
