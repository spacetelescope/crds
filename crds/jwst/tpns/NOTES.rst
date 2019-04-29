Other Notes
-----------

#1 - IRS2 readouts and 2048x3200
................................

NIRSpec IRS2 readouts produce 3200 pixels in one image dimension. In the native
detector readout orientation it's nx=3200, ny=2048 (i.e. it's a horizontal
rectangle). But all science data and all reference data in CRDS always need to
be in DMS (science) orientation, which for NIRSpec means the x/y axes get
swapped, so that means IRS2 images have nx=2048, ny=3200 (i.e. a vertical
rectangle). Taking a quick look at one of the NIRSpec MASK ref files in CRDS
for IRS2 mode, it correctly shows that the image has dimensions of
2048x3200. So that's the correct orientation you're looking for. If anyone ever
delivers a NIRSpec ref file to CRDS that has dimensions 3200x2048, it's wrong
(it's still in native detector orientation) and needs to be rejected.

The complicating factor in all of this is that a conscious decision was made to
still have the SUBSTRTn keywords (datamodel meta.subarray.[xy]size) retain
their original values of 2048, rather than 3200, because the extra pixels in
the image do not correspond to real pixels on the detector (they're virtual
values inserted into the image). So the detector was still commanded to readout
2048x2048 pixels, hence the decision to make the size keywords still say
2048x2048. Even though ny=3200 in the actual image. So any comparison of
subarray size keyword values against the actual image size needs to allow for
this (i.e. it's OK to have meta.subarray.ysize=2048 when data.shape[-2] =
3200), as long as READPATT has the string "IRS2" somewhere in it.

#2 - SUBSTRT 1/2 & reference pixels
...................................

For the JWST detectors all reference pixels are physical pixels that are
counted as part of the detector dimensions (unlike virtual overscan regions
in CCD's). So the 2048x2048 detector dimensions of the near-IR detectors
already includes the reference pixels and the MIRI detectors are always
referenced in the full 1032x1024 space that includes their reference
pixels. The SUBSTRTn and SUBSIZEn values also always include the reference
pixels (i.e. SUBSTRT1 = 1 means the subarray is starting on the first
reference pixel. The first "live" pixel is at SUBSTRT1 = 5.) So for MIRI
full-frame readouts SUBSIZE1 = 1032, not 1024 (the same as NAXIS1).

The only exception to this is the NIRSpec IRS2 readout mode that includes
many more columns of reference pixels interspersed within the live pixels,
resulting in total image dimensions that are greater than 2048 (at least
along the y image axis). So this is the only case where SUBSIZEn != NAXISn,
because NAXIS2 2048, while a decision was made to still set SUBSIZE2 = 2048.


# 3 - DARK array NDIM
.....................

Comments about array dimensions and array shape equivalence:

DARK: non-MIRI: SCI=ERR=3D, DQ=2D; MIRI: SCI=ERR=DQ=4D

LINEARITY: COEFFS=3D, DQ=2D

# 4 - NIRSPEC DARK no reference pixels
......................................

For NIRSpec data, the DARK step is run (in calwebb_detector1.py) after
refpix, so the image at that point will be 2048 x 2048, and the dark file will
have shape (N, 2048, 2048), where N has to do with the number of groups.  So it
is correct that the darks will be 2048x2048.

Similarly for READNOISE.

# 5 - NIRSPEC SUBARRAY GAIN=2 STRIPING
......................................

If memory serves, in a conversation we all had with NIRSpec folks about a year
ago, they need to deliver some subarray ref files with SUBARRAY='GENERIC',
because the exact placement of the subarray varies from exposure to exposure
and is tied to the use of different gratings (different gratings result in
spectra being located in slightly different places on the detector and they
change the subarray location to match). So for example the "mystery stripe"
2048x256 subarray is probably used for fixed-slit exposures, where the 256 is
large enough to cover all the slits. Science exposures taken using a subarray
for a single slit (which is smaller yet) will use that 2048x256 reference file
and extract (on the fly) the subarray that matches the smaller science
subarray, matching both the location and size of the subarray used in the
science exposure. So that's why SUBARRAY has to be set to 'GENERIC' in those
ref files, so that CRDS knows to select it when a science exposure uses some
other specific subarray like "SUBS200A1" or "SUBS400A1" and let the cal
pipeline do the on-the-fly extraction thing, like it also does when full-frame
ref files use SUBARRAY='GENERIC'.

The reason they can't just use a full-frame ref file with SUBARRAY='GENERIC'
for these, is because NIRSpec subarrays are readout using a different gain than
full-frame, so they have to use subarray-specific reference files (because the
actual pixel values in the images are different than for full-frame).

# 6 - GAIN SCI HDU and GAINFACT
...............................

The GainModel schema specifies a single FITS HDU with EXTNAME='SCI'. The jump
and ramp_fit steps, which use the gain ref file, both load it into a GainModel
data model, hence if there isn't a SCI extension present I would assume the
load would fail. Therefore the SCI label should be mandatory.

The GAINFACT keyword is only used (and hence required) for NIRSpec gain ref
files that are subarray (like jwst_nirspec_gain_0016.fits and
jwst_nirspec_gain_0017.fits). So GAINFACT is only needed when the ref data have
dimensions less than 2048x2048.

# 7 - AREA MIRI SCI dimensions
..............................

Huh, never noticed this before, which is due to the fact that all we do with
the imaging-mode AREA reference files is attach the data array to an extra
extension in the science product and that's it - we don't actually use it or
apply it anywhere. It's information only, for possible use by the user while
doing analysis. The reference pixels don't get stripped off until level-3
processing, which combines multiple images. Level-2 products, which is the
stage where a user might need to use the AREA data, still have the reference
pixels in the image. So theoretically I guess the AREA array should be the
original 1032x1024 size that includes the reference pixels, just for ease in
applying it to the science image, which will still be 1032x1024 at that point.

AREA ref files for the imaging mode of other instruments, like NIRCam, are the
full 2048x2048 size, which means they contain reference pixels. Hence for
consistency we should request that the MIRI IDT deliver theirs the same way.

