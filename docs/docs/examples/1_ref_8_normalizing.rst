.. _normalizing-source-flux:

Normalizing the Source Flux
---------------------------

Regardless of whether you use your own input spectrum, a standard
spectrum, or a modeled spectrum, you may wish to renormalize the
source&rsquo;s brightness. Sources can be normalized either to a specified
magnitude within a given band or to a specified flux density (:math:`erg \cdot cm^{-2} \cdot s^{-1} \cdot \AA^{-1}`)
value at a given wavelength. When normalizing to flux at a given wavelength, it is
necessary to choose a wavelength for which the source flux is
non-zero, but it is not necessary to choose a wavelength within the
pass band of the instrument's observation mode.

Total flux, Vega magnitudes, or GALEX (AB) magnitudes are used for point sources. Flux,
Vega magnitudes, or GALEX (AB) magnitudes per square arc second are used for extended/diffuse
sources, and the brightness is considered to be uniform. For
instruments that have global count rate limits (MAMA detectors, for
example), the radius of the source in arc seconds should be
specified. This allows the ETC to estimate the global count rate and
to properly check the global count rate limit.

When using a user supplied or HST calibrated spectrum, it is not
necessary to renormalize. Select the *Do not renormalize*
option on the form, in which case the input file will be assumed to
have the correct units (:math:`erg \cdot cm^{-2} \cdot s^{-1} \cdot \AA^{-1}`)
for point sources and [:math:`erg \cdot cm^{-2} \cdot sec^{-1} \cdot \AA^{-1} \cdot arcsec^{-2}`] 
for diffuse sources.

The bands supported by the ETC can be found below:

- **Johnson:** U, B, V, R, I, J, K
- **Bessell:** H, J, K
- **Cousins:** R, I
- **NICMOS:** F110W, F160W
- **GALEX:** FUV, NUV
- **Sloan:** G, R, I, Z

