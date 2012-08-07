Basic Use
---------

Using the ETC is quite simple. Once you have traversed to the desired ETC web
page based on the instrument and science mode, simply enter the specified
parameters for each of the sections listed below, then click the "Submit"
button to retrieve your results. 

 - Instrument settings
 - Exposure parameters 
      - Time or SNR
      - Observation wavelength (for spectroscopy)
      - Point or extended target
      - Photometric extraction region
 - Target (source) specification
      - spectral distribution
      - extinction
      - redshift
      - emission lines
      - flux normalization
 - Expected background levels
      - earthshine
      - zodiacal light
      - airglow (geo-coronal) lines

All the sections contain preloaded defaults, so
at any point you can submit the current settings for an ETC calculation. 


Examining the Results
---------------------

Detailed Results
~~~~~~~~~~~~~~~~

The results page includes the basic calculation results (time or SNR requested), detailed results with rates, counts, and noise associated with each component, and any relevant warnings about the calculation. For convenience, the input values are then summarized.

 Most of the detailed results are self-explanatory but a few items warrant additional explanation:


Spectroscopy: Regions for Rate and Counts
.........................................

For spectroscopic calculations, the rate (column 1) and counts (column 2) are reported over different regions:


 - the number of *counts* (column 2) is reported over the specified extraction region used for the SNR calculation, which is H pixels high and one resel (resolution element) wide. The size of the resel in pixels is reported in the heading of column 2.

 - the count *rate* (column 1) is reported over an area H pixels high by 1 pixel wide



Brightest Pixel Rate and Counts
...............................

In calculations for which the detector parameters specify that the exposure should be divided into independent exposures (by setting # frames or CR-Split), the entire time will be used for most results, but the divided time (total_time/nframes) will be used to compute the number of counts in the brightest pixel calculation, so that it can be checked against the saturation limit. This can lead to the counter-intuitive result in which the number of counts in the brightest pixel is smaller than the count rate in the brightest pixel.


Plots and Tables
~~~~~~~~~~~~~~~~

Buttons appear near the bottom of the page for viewing available plots.

All the ETCs present plots of the throughput of the specified instrument configuration, and of the input spectrum prior to observation, with flux units in *flam*. After initial display, the X and Y ranges can be specified and the data re-plotted with the new values. This allows the user to zoom in on a region of interest, or shift a region of interest out from under the legend of a plot with multiple curves.

Spectroscopic Plots and Tables
..............................

The SNR and Total Counts plots that are available for spectroscopic modes present the results over the extraction region (H pixels high by 1 resel wide) as a funciton of wavelength. Thus, the SNR plot is consistent with the reported (or input) scalar SNR.

The table that is available for spectroscopic modes presents the results in counts over an area that is H pixels high by 1 pixel wide. Thus, the table is not consistent with the plots.
