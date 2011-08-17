Calculations
============

**Exposure Time and S/N Calculation**

To specify the exposure parameters, you can give either the exposure time (in
seconds), in which case the program will calculate the count rates due to the
source, background, and the resulting S/N ratio. Or, you can give the required
S/N ratio, in which case the program will calculate the required exposure time
to achieve this S/N ratio and the corresponding integrated counts. Further
details follow:

**If you select the exposure time:**

The program takes the filter transmission, throughputs of the optics and the
efficiency of the detector, and calculates the expected countrate for the
specified instrument configuration and finds the S/N ratio and the integrated
counts from the source, the sky background, and the detector background for the
specified exposure time.

**If you select the S/N ratio:**

The ETC takes the filter transmission, throughputs of the optics and the
efficiency of the detector, and calculates the expected count rate for the
specified instrument configuration and finds the required exposure time so that
the observation will have the specified S/N. This exposure time is then used to
calculate the integrated counts from the source and different backgrounds.

**Specifying the Wavelength (spectroscopic exposures):**

The S/N and associated counts values listed on the main output page are
calculated at a specified wavelength, sometimes called the **observation
wavelength**. The observation wavelength must be in the inclusive throughput
range for the instrument, detector, spectral element(s) and disperser central
wavelength (if applicable) chosen for this observation.


.. toctree::
   :maxdepth: 1
   
   1_2_1_snr.rst
   1_2_2_time.rst

