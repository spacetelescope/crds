Reference File Conventions
==========================

Supported CRDS file formats
---------------------------

  - FITS
  - ASDF
  - JSON
  - YAML

Required Keywords and Properties
--------------------------------

Reference files specify metadata as keyword values that CRDS often checks.  In
general, instrument configuration parameters can be used to automatically add
reference files to CRDS rmaps which describe how to assign them.  In essence,
each reference file is required to specify the instrument configurations for
which it is the best reference file.  CRDS supports the use of patterns and/or
substitutions for keyword values which enable as single reference file to
support more than one instrument configuration.

Keywords For New File Formats
.............................
 
Newer file formats used for JWST and Roman such as ASDF and JSON have equivalent
"keywords" that are generally organized hierarchically in a reference's
metadata tree.

.. tabs::

   .. group-tab:: JWST

      For JWST, the calibration code defines file format schema which show the correspondence between "data model path" and more primitive representations like FITS keywords: `Data Models Schema <https://github.com/spacetelescope/stdatamodels/tree/main/src/stdatamodels/jwst/datamodels/schemas>`_. 
      
      The schema also describe related facts such as parameter type and valid values.  For instance, the model path:

        .. code-block:: python

            META.INSTRUMENT.DETECTOR

      is equivalent to the FITS keyword:

        .. code-block:: python

            DETECTOR

      while:

        .. code-block:: python

            META.INSTRUMENT.NAME

      corresponds to the FITS keyword:

        .. code-block:: python

            INSTRUME

      To isolate CRDS from physical file formats for JWST, CRDS generally uses datamodel paths to refer to metadata; by convention CRDS converts them to all uppercase.

      For ASDF, the equivalent metadata might be hierarchically encoded as:

        .. code-block:: python

            meta:
                instrument:
                    detector: NRS1
                    name: NIRSPEC

      In this case, the keyword `DETECTOR` does not exist at all in ASDF, but the model path still does.

   .. group-tab:: ROMAN

      Roman calibration code defines the file format schema of `.asdf` files via `Roman Datamodels`. To isolate CRDS from physical file formats for Roman, CRDS generally uses datamodel paths to refer to metadata; by convention CRDS converts them to all uppercase. For example, the file metadata might be hierarchically encoded as

        .. code-block:: python

            roman:
                meta:
                    instrument:
                        detector: WFI01
                        name: WFI

      For CRDS, this is equivalent to:

        .. code-block:: python
            
            'ROMAN.META.INSTRUMENT.NAME': 'WFI'
            'ROMAN.META.INSTRUMENT.DETECTOR': 'WFI01'


Boilerplate Keywords
....................

Each mission defines a small set of required keywords for reference file provenance information:

.. tabs::

   .. group-tab:: HST

       .. table:: Boiler Plate Keywords
        :widths: auto
        
        ===============  =====================
        FITS             VALUES
        ===============  =====================
        TELESCOP         HST
        INSTRUME         ACS
        FILETYPE         BIAS
        USEAFTER         2017-10-01T00:00:00
        PEDIGREE         DUMMY, GROUND, IN FLIGHT
        HISTORY          File creation notes
        COMMENT          Additional notes
        DESCRIP          Brief description
        ===============  =====================

   .. group-tab:: JWST

       .. table:: Boiler Plate Keywords
        :widths: auto
        
        ===============  ====================   =====================
        FITS             DATAMODELS             VALUES
        ===============  ====================   =====================
        TELESCOP         META.TELESCOPE         JWST
        INSTRUME         META.INSTRUMENT.NAME   MIRI
        REFTYPE          META.REFERENCE.TYPE    DARK
        USEAFTER         META.USEAFTER          2017-10-01T00:00:00
        AUTHOR           META.AUTHOR            Homer Simpson
        PEDIGREE         META.PEDIGREE          DUMMY, GROUND, IN FLIGHT
        HISTORY          META.HISTORY           File creation notes
        DESCRIP          META.DESCRIPTION       Brief description
        ===============  ====================   =====================

   .. group-tab:: ROMAN

       .. table:: Boiler Plate Keywords
        :widths: auto
        
        ==========================   =====================
        ROMAN_DATAMODELS             VALUES
        ==========================   =====================
        ROMAN.META.TELESCOPE         ROMAN
        ROMAN.META.INSTRUMENT.NAME   MIRI
        ROMAN.META.REFERENCE.TYPE    DARK
        ROMAN.META.USEAFTER          2017-10-01T00:00:00
        ROMAN.META.AUTHOR            Homer Simpson
        ROMAN.META.PEDIGREE          DUMMY, GROUND, IN FLIGHT
        ROMAN.META.HISTORY           File creation notes
        ROMAN.META.DESCRIPTION       Brief description
        ==========================   =====================


Matching Keyword Patterns
.........................

To support automatic rmap updates, any keyword used to assign best references
must be added to the reference metadata.  For example, if a FITS reference type
uses `DETECTOR` to help assign a reference in the rmap, the reference file is
*required* to define `DETECTOR` or `P_DETECT`.

Discrete/Real Values
++++++++++++++++++++

Very often the applicability of a reference file can be defined by a single
discrete real world value, or by a simple one word wild card such as `ANY` or
`N/A`:

  .. code-block:: python
    
      META.INSTRUMENT.DETECTOR = NRS1

Where applicable, a discrete valued keyword will describe the instrument
configuration used to create the reference file.


Conditional Pattern Substitutions
+++++++++++++++++++++++++++++++++

Sometimes it is useful to apply one reference file to a number of specific real
world keyword values, i.e. some limited set of readout patterns, not merely the
single valued instrument configuration used to obtain the reference data.

.. tabs::

   .. group-tab:: HST

      HST used hidden substitution rules built into CDBS and CRDS to describe patterns of values not suitable for FITS keywords:

        .. code-block:: python

            {'acs': {
                'APERTURE': {
                    "DETECTOR=='WFC' and APERTURE=='ANY_FULL' and DATE_OBS < '2016-09-25'": 'NONE|WFC|WFC-FIX|WFC1|WFC1-CTE|WFC1-FIX|WFC1-IRAMP|WFC1-MRAMP|WFC2|WFC2-FIX|WFC2-MRAMP|WFC2-ORAMP|WFCENTER|WFC1A-512|WFC1B-512|WFC2C-512|WFC2D-512|WFC1A-1K|WFC1B-1K|WFC2C-1K|WFC2D-1K|WFC1A-2K|WFC1B-2K|WFC2C-2K|WFC2D-2K', 
                    "DETECTOR=='WFC' and APERTURE=='ANY_FULL' and DATE_OBS >= '2016-09-25'": 'NONE|WFC|WFC-FIX|WFC1|WFC1-CTE|WFC1-FIX|WFC1-IRAMP|WFC1-MRAMP|WFC2|WFC2-FIX|WFC2-MRAMP|WFC2-ORAMP|WFCENTER|WFC1A-512|WFC1B-512|WFC2C-512|WFC2D-512|WFC1A-1K|WFC1B-1K|WFC2C-1K|WFC2D-1K|WFC1A-2K|WFC1B-2K|WFC2C-2K|WFC2D-2K|WFC1-POL0V|WFC1-POL60V|WFC1-POL120V|WFC1-POL0UV|WFC1-POL60UV|WFC1-POL120UV|WFC1-IRAMPQ|WFC1-MRAMPQ|WFC2-MRAMPQ|WFC2-ORAMPQ|WFC1-SMFL|WFC2-SMFL',
                    "DETECTOR=='WFC' and APERTURE=='ANY_WFC1_2K' and DATE_OBS < '2016-09-25'": 'WFC1-2K|WFC1-POL0UV|WFC1-POL0V|WFC1-POL120UV|WFC1-POL120V|WFC1-POL60UV|WFC1-POL60V|WFC1-IRAMPQ|WFC1-MRAMPQ|WFC1-SMFL',
                    "DETECTOR=='WFC' and APERTURE=='ANY_WFC1_2K' and DATE_OBS >= '2016-09-25'": 'WFC1-2K',
                    "DETECTOR=='WFC' and APERTURE=='ANY_WFC2_2K' and DATE_OBS < '2016-09-25'": 'WFC2-2K|WFC2-POL0UV|WFC2-POL0V|WFC2-POL120UV|WFC2-POL120V|WFC2-POL60UV|WFC2-POL60V|WFC2-MRAMPQ|WFC2-ORAMPQ|WFC2-SMFL',
                    "DETECTOR=='WFC' and APERTURE=='ANY_WFC2_2K' and DATE_OBS >= '2016-09-25'": 'WFC2-2K',
                },
                'CCDAMP': {
                    "DETECTOR=='HRC' and CCDAMP=='ANY'": 'A|ABCD|AD|B|BC|C|D',
                    "DETECTOR=='WFC' and CCDAMP=='ABCDALL'": 'A|ABCD|B|C|D',
                    "DETECTOR=='WFC' and CCDAMP=='ANY'": 'A|ABCD|AD|B|BC|C|D',
                },
                'CCDGAIN': {
                    "DETECTOR=='HRC' and CCDGAIN=='-1'": '1.0|2.0|4.0|8.0',
                    "DETECTOR=='WFC' and CCDGAIN=='-1'": '0.5|1.0|1.4|2.0',
                    "DETECTOR in ['WFC', 'HRC'] and CCDGAIN=='-999'": '1.0|2.0|4.0|8.0',
                    "DETECTOR in ['WFC', 'HRC'] and CCDGAIN=='-999.0'": '1.0|2.0|4.0|8.0',
                },
                'FILTER1': {
                    "DETECTOR=='HRC' and FILTER1=='ANY'": 'CLEAR1S|F475W|F502N|F550M|F555W|F606W|F625W|F658N|F658N|F775W|F850LP|F892N|G800L|POL0UV|POL120UV|POL60UV',
                    "DETECTOR=='SBC' and FILTER1=='ANY' and OBSTYPE=='IMAGING'": 'BLOCK1|BLOCK2|BLOCK3|BLOCK4|F115LP|F122M|F125LP|F140LP|F150LP|F165LP',
                    "DETECTOR=='SBC' and FILTER1=='ANY' and OBSTYPE=='SPECTROSCOPIC'": 'PR110L|PR130L',
                    "DETECTOR=='WFC' and FILTER1=='ANY'": 'CLEAR1L|F475W|F502N|F550M|F555W|F606W|F625W|F658N|F775W|F850LP|F892N|G800L|POL0UV|POL120UV|POL60UV'
                },
                'FILTER2': {
                    "DETECTOR=='HRC' and FILTER2=='ANY'": 'CLEAR2L|CLEAR2S|F220W|F250W|F330W|F344N|F435W|F660N|F814W|FR388N|FR459M|FR505N|FR656N|FR914M|POL0V|POL120V|POL60V|PR200L',
                    "DETECTOR=='WFC' and FILTER2=='ANY'": 'CLEAR2L|F330W|F435W|F660N|F814W|FR1016N|FR388N|FR423N|FR459M|FR462N|FR505N|FR551N|FR601N|FR647M|FR656N|FR716N|FR782N|FR853N|FR914M|FR931N|POL0V|POL120V|POL60V'
                },
                'FLASHCUR': {"FLASHCUR=='ANY'": 'HIGH|LOW|MED'},
                'LRFWAVE' : {
                    "LRFWAVE == '3774.0'" : 'between 3710 3826',
                    "LRFWAVE == '3880.0'" : 'between 3826 3936',
                    "LRFWAVE == '3992.0'" : 'between 3936 4051',
                    "LRFWAVE == '4105.0'" : 'between 4051 4167',
                    "LRFWAVE == '4230.0'" : 'between 4167 4296',
                    "LRFWAVE == '4362.0'" : 'between 4296 4421',
                    "LRFWAVE == '4488.0'" : 'between 4421 4554',
                    "LRFWAVE == '4620.0'" : 'between 4554 4686',
                    "LRFWAVE == '4752.0'" : 'between 4686 4821',
                    "LRFWAVE == '5038.0'" : 'between 4821 5271',
                    "LRFWAVE == '5491.0'" : 'between 5271 5751',
                    "LRFWAVE == '5998.0'" : 'between 5751 6271',
                    "LRFWAVE == '6505.0'" : 'between 6271 6851',
                    "LRFWAVE == '7205.0'" : 'between 6851 7471',
                    "LRFWAVE == '7836.0'" : 'between 7471 8161',
                },
              'OBSTYPE': {
                  "DETECTOR=='HRC' and FILTER1=='G800L' and OBSTYPE=='ANY'": 'CORONAGRAPHIC|IMAGING'
              },
              'NAXIS1': {"DETECTOR=='WFC' and APERTURE=='ANY_FULL'": 'ANY',},
              'NAXIS2': {"DETECTOR=='WFC' and APERTURE=='ANY_FULL'": 'ANY',},
              'LTV1': {"DETECTOR=='WFC' and APERTURE=='ANY_FULL'": 'ANY',},
              'LTV2': {"DETECTOR=='WFC' and APERTURE=='ANY_FULL'": 'ANY',},
              'SHUTRPOS': {"SHUTRPOS=='ANY'": 'A|B'},
            },
            'cos': {
                'LIFE_ADJ': {
                    "LIFE_ADJ=='-11'": '-1.0|1.0',
                    "LIFE_ADJ=='-11.0'": '-1.0|1.0'
                },
                'OPT_ELEM': {
                    "DETECTOR=='FUV' and OPT_ELEM=='ANY'": 'G130M|G140L|G160M',
                    "DETECTOR=='NUV' and OPT_ELEM=='ANY'": 'G185M|G225M|G230L|G285M|MIRRORA|MIRRORB'
                }
            },
            'stis': {
                'APERTURE': {
                    "OBSTYPE=='IMAGING' and OPT_ELEM=='MIRCUV' and APERTURE=='ANY'": '25MAMA|2X2|6X6|F25NDQ1|F25NDQ2|F25NDQ3|F25NDQ4',
                    "OBSTYPE=='IMAGING' and OPT_ELEM=='MIRFUV' and APERTURE=='ANY'": 'F25LYA|F25ND3|F25ND5|F25NDQ|F25NDQ1|F25NDQ2|F25NDQ3|F25NDQ4|F25QTZ|F25SRF2',
                    "OBSTYPE=='IMAGING' and OPT_ELEM=='MIRNUV' and APERTURE=='ANY'": '25MAMA|2X2|6X6|F25CIII|F25CN182|F25CN270|F25MGII|F25ND3|F25ND5|F25NDQ|F25NDQ1|F25NDQ2|F25NDQ3|F25NDQ4|F25QTZ|F25SRF2',
                    "OBSTYPE=='IMAGING' and OPT_ELEM=='MIRVIS' and APERTURE=='ANY'": '0.05X29|0.05X31NDA|0.05X31NDB|0.09X29|0.1X0.03|0.1X0.06|0.1X0.09|0.1X0.2|0.2X0.05ND|0.2X0.06|0.2X0.06FPA|0.2X0.06FPB|0.2X0.06FPC|0.2X0.06FPD|0.2X0.06FPE|0.2X0.09|0.2X0.2|0.2X0.2FPA|0.2X0.2FPB|0.2X0.2FPC|0.2X0.2FPD|0.2X0.2FPE|0.2X0.5|0.2X29|0.3X0.05ND|0.3X0.06|0.3X0.09|0.3X0.2|0.5X0.5|1X0.06|1X0.2|25MAMA|2X2|31X0.05NDA|31X0.05NDB|31X0.05NDC|36X0.05N45|36X0.05P45|36X0.6N45|36X0.6P45|50CCD|50CORON|52X0.05|52X0.05F1|52X0.05F2|52X0.1|52X0.1B0.5|52X0.1B1.0|52X0.1B3.0|52X0.1F1|52X0.1F2|52X0.2|52X0.2F1|52X0.2F2|52X0.5|52X0.5F1|52X0.5F2|52X2|52X2F1|52X2F2|6X0.06|6X0.2|6X0.5|6X6|F25CIII|F25CN182|F25CN270|F25LYA|F25MGII|F25ND3|F25ND5|F25NDQ|F25NDQ1|F25NDQ2|F25NDQ3|F25NDQ4|F25QTZ|F25SRF2|F28X50LP|F28X50OII|F28X50OIII'
                },
                'CCDAMP': {"CCDAMP=='ANY'": 'A|B|C|D'},
                'CCDGAIN': {"CCDGAIN=='-1'": '1.0|2.0|4.0|8.0'},
                'CENWAVE': {
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='E140H' and CENWAVE=='-1'": '1234.0|1271.0|1307.0|1343.0|1380.0|1416.0|1453.0|1489.0|1526.0|1562.0|1598.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='E140M' and CENWAVE=='-1'": '1425.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='E230H' and CENWAVE=='-1'": '1763.0|1813.0|1863.0|1913.0|1963.0|2013.0|2063.0|2113.0|2163.0|2213.0|2263.0|2313.0|2363.0|2413.0|2463.0|2513.0|2563.0|2613.0|2663.0|2713.0|2762.0|2812.0|2862.0|2912.0|2962.0|3012.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='E230M' and CENWAVE=='-1'": '1978.0|2124.0|2269.0|2415.0|2561.0|2707.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G140L' and CENWAVE=='-1'": '1425.0|1575.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G140M' and CENWAVE=='-1'": '1173.0|1218.0|1222.0|1272.0|1321.0|1371.0|1387.0|1400.0|1420.0|1470.0|1518.0|1540.0|1550.0|1567.0|1616.0|1640.0|1665.0|1714.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G230L' and CENWAVE=='-1'": '2376.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G230LB' and CENWAVE=='-1'": '2375.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G230M' and CENWAVE=='-1'": '1687.0|1769.0|1851.0|1884.0|1933.0|2014.0|2095.0|2176.0|2257.0|2338.0|2419.0|2499.0|2579.0|2600.0|2659.0|2739.0|2800.0|2818.0|2828.0|2898.0|2977.0|3055.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G230MB' and CENWAVE=='-1'": '1713.0|1854.0|1995.0|2135.0|2276.0|2416.0|2557.0|2697.0|2794.0|2836.0|2976.0|3115.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G430L' and CENWAVE=='-1'": '4300.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G430M' and CENWAVE=='-1'": '3165.0|3305.0|3423.0|3680.0|3843.0|3936.0|4194.0|4451.0|4706.0|4781.0|4961.0|5093.0|5216.0|5471.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G750L' and CENWAVE=='-1'": '7751.0|8975.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='G750M' and CENWAVE=='-1'": '10363.0|5734.0|6094.0|6252.0|6581.0|6768.0|7283.0|7795.0|8311.0|8561.0|8825.0|9286.0|9336.0|9806.0|9851.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='PRISM' and CENWAVE=='-1'": '1200.0|2125.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='X140H' and CENWAVE=='-1'": '1232.0|1269.0|1305.0|1341.0|1378.0|1414.0|1451.0|1487.0|1523.0|1560.0|1587.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='X140M' and CENWAVE=='-1'": '1425.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='X230H' and CENWAVE=='-1'": '1760.0|1810.0|1860.0|1910.0|1960.0|2010.0|2060.0|2110.0|2160.0|2210.0|2261.0|2310.0|2360.0|2410.0|2460.0|2511.0|2560.0|2610.0|2660.0|2710.0|2760.0|2810.0|2860.0|2910.0|2960.0|3010.0',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='X230M' and CENWAVE=='-1'": '1975.0|2122.0|2268.0|2414.0|2560.0|2703.0'
                },
                'DETECTOR': {"DETECTOR=='ANY'": 'CCD|FUV-MAMA|NUV-MAMA'},
                'OBSTYPE': {"OBSTYPE=='ANY'": 'IMAGING|SPECTROSCOPIC'},
                'OPT_ELEM': {
                    "OBSTYPE=='IMAGING' and OPT_ELEM=='ANY'": 'MIRCUV|MIRFUV|MIRNUV|MIRVIS',
                    "OBSTYPE=='SPECTROSCOPIC' and OPT_ELEM=='ANY'": 'E140H|E140M|E230H|E230M|G140L|G140M|G230L|G230LB|G230M|G230MB|G430L|G430M|G750L|G750M|PRISM|X140H|X140M|X230H|X230M'
                }
            },
            'wfc3': {
                'APERTURE': {
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='CHIP1_SUB_NOCORNERS'": 'UVIS1-2K4-SUB|UVIS1-M512-SUB',
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='CHIP2_SUB_NOCORNERS'": 'UVIS2-2K4-SUB|UVIS2-M512-SUB',
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='CUSTOM_SUBARRAYS'": 'G280-REF|UVIS|UVIS-CENTER|UVIS-FIX|UVIS-QUAD|UVIS-QUAD-FIX|UVIS1|UVIS1-FIX|UVIS2|UVIS2-FIX',
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='FULLFRAME_2AMP'": 'UVIS|UVIS-CENTER|UVIS-FIX|UVIS1|UVIS1-FIX|UVIS2|UVIS2-FIX',
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='FULLFRAME_4AMP'": 'G280-REF|UVIS|UVIS-CENTER|UVIS-FIX|UVIS-IR-FIX|UVIS-QUAD|UVIS-QUAD-FIX|UVIS1|UVIS1-FIX|UVIS2|UVIS2-FIX|UVIS2-C512C-CTE|UVIS2-C1K1C-CTE',
                    "DETECTOR=='UVIS' and BINAXIS1=='1' and BINAXIS2=='1' and APERTURE=='QUAD_CORNER_SUBARRAYS'": 'UVIS-QUAD-SUB|UVIS1-2K2A-SUB|UVIS1-2K2B-SUB|UVIS1-C512A-SUB|UVIS1-C512B-SUB|UVIS2-2K2C-SUB|UVIS2-2K2D-SUB|UVIS2-C1K1C-SUB|UVIS2-C512C-SUB|UVIS2-C512D-SUB|UVIS2-M1K1C-SUB|UVIS2-M512C-SUB',
                    "DETECTOR=='UVIS' and BINAXIS1=='2' and BINAXIS2=='2' and APERTURE=='ANY'": 'G280-REF|UVIS|UVIS-CENTER|UVIS-FIX|UVIS-IR-FIX|UVIS-QUAD|UVIS-QUAD-FIX|UVIS1|UVIS1-FIX|UVIS2|UVIS2-FIX',
                    "DETECTOR=='UVIS' and BINAXIS1=='3' and BINAXIS2=='3' and APERTURE=='ANY'": 'G280-REF|UVIS|UVIS-CENTER|UVIS-FIX|UVIS-IR-FIX|UVIS-QUAD|UVIS-QUAD-FIX|UVIS1|UVIS1-FIX|UVIS2|UVIS2-FIX'
                },
                'CCDAMP': {
                    "CCDAMP=='ANY'": 'A|ABCD|AC|AD|B|BC|BD|C|D',
                    "CCDAMP=='SINGLE_AMP'": 'A|B|C|D'
                },
                'CCDGAIN': {
                    "DETECTOR=='IR' and CCDGAIN=='-1'": '2.0|2.5|3.0|4.0',
                    "DETECTOR=='IR' and CCDGAIN=='-1.'": '2.0|2.5|3.0|4.0',
                    "DETECTOR=='UVIS' and CCDGAIN=='-1'": '1.0|1.5|2.0|4.0',
                    "DETECTOR=='UVIS' and CCDGAIN=='-1.'": '1.0|1.5|2.0|4.0'
                },
                'CHINJECT': {"CHINJECT=='ANY'": 'CONT|LINE10|LINE17|LINE25|NONE'},
                'FILTER': {
                    "DETECTOR=='IR' and FILTER=='ANY'": 'BLANK|F093W|F098M|F105W|F110W|F125W|F126N|F127M|F128N|F130N|F132N|F139M|F140W|F153M|F160W|F164N|F167N',
                    "DETECTOR=='UVIS' and FILTER=='ANY'": 'CLEAR|F200LP|F218W|F225W|F275W|F280N|F300X|F336W|F343N|F350LP|F373N|F390M|F390W|F395N|F410M|F438W|F467M|F469N|F475W|F475X|F487N|F502N|F547M|F555W|F588N|F600LP|F606W|F621M|F625W|F631N|F645N|F656N|F657N|F658N|F665N|F673N|F680N|F689M|F763M|F775W|F814W|F845M|F850LP|F953N|FQ232N|FQ243N|FQ378N|FQ387N|FQ422M|FQ436N|FQ437N|FQ492N|FQ508N|FQ575N|FQ619N|FQ634N|FQ672N|FQ674N|FQ727N|FQ750N|FQ889N|FQ906N|FQ924N|FQ937N'
                },
                'SAMP_SEQ': {
                    "SAMP_SEQ=='ANY'": 'MIF1200|MIF1500|MIF600|MIF900|NONE|RAPID|SPARS10|SPARS100|SPARS200|SPARS25|SPARS350|SPARS50|STEP100|STEP200|STEP25|STEP400|STEP50|UNKNOWN'
                }
              }
            }

      The HST substition patterns above are of the form:

        .. code-block:: python

            <instrument>
                <keyword>
                  <condition1> : <substitution1>
                  <condition2> : <substitution2>
                  ...
      
      For each rmap update for *instrument*,  for each matching *keyword*, each *condition* is evaluated with respect to the reference file header.  If the *condition* is *True* then the corresponding *substitution* is used to replace the value of *keyword* for the purposes of updating the rmap.

   .. group-tab:: JWST

      JWST uses a more explicit approach where patterns are specified directly via reference metadata.  The CAL code data models define optional keywords beginning with *P_* that can have or-ed values. For instance, in FITS parlance:

        .. code-block:: python
          
            P_DETECT = NRCA1 | NRCA4 |

      means that the reference file should be used for both `DETECTOR=NRCA1` and `DETECTOR=NRCA4`.  Typically the *P_* keyword name is truncated to the FITS 8 character limit as needed.

      The trailing `|` is required to satisfy the calibration code data model
      schema checks of allowed patterns.
      
      If no pattern keyword is defined, CRDS will use the equivalent normal keyword specified to update the matching rules. In terms of datamodels paths, the above value would be specified similarly:

        .. code-block:: python
            
            META.INSTRUMENT.P_DETECTOR = NRCA1 | NRCA4 |
      
      The following table defines the pattern keywords currently supported for JWST:

      .. table:: JWST Pattern Keyword Names
              :widths: auto
              
              =========   =========== ===========================
              FITS        ``P_`` FITS ``P_`` DATAMODELS
              =========   =========== ===========================
              EXP_TYPE    P_EXP_TY    META.EXPOSURE.P_EXPTYPE
              BAND        P_BAND      META.INSTRUMENT.P_BAND
              DETECTOR    P_DETECT    META.INSTRUMENT.P_DETECTOR
              CHANNEL     P_CHANNE    META.INSTRUMENT.P_CHANNEL
              FILTER      P_FILTER    META.INSTRUMENT.P_FILTER
              GRATING     P_GRATIN    META.INSTRUMENT.P_GRATING
              PUPIL       P_PUPIL     META.INSTRUMENT.P_PUPIL
              MODULE      P_MODULE    META.INSTRUMENT.MODULE
              SUBARRAY    P_SUBARR    META.SUBARRAY.P_SUBARRAY
              READPATT    P_READPA    META.EXPOSURE.P_READPATT
              =========   =========== ===========================
      
      Each ``P_`` keyword is explicitly defined in CRDS code as well as the CAL code
      data models.  Relative to HST substitutions, the advantage of the JWST ``P_``
      keywords is that the pattern values can be defined in arbitrary combinations
      in the reference files instead of CRDS code.

   .. group-tab:: ROMAN

      Roman uses the more explicit approach where patterns are specified directly via reference metadata.  Roman datamodels code defines optional keywords beginning with *P_* that can have or-ed values. For instance, in ASDF parlance:

        .. code-block:: python
          
            P_OPTICAL_ELEMENT = F213 | F158 |

      means that the reference file should be used for both `OPTICAL_ELEMENT=F213` and `OPTICAL_ELEMENT=F158`.

      The trailing `|` is required to satisfy the calibration code data model schema checks of allowed patterns.
      
      If no pattern keyword is defined, CRDS will use the equivalent normal keyword specified to update the matching rules. In terms of datamodels paths, the above value would be specified similarly:

        .. code-block:: python
            
            roman.meta.instrument.p_optical_element = F213 | F158 |
      
      The following table defines the pattern keywords currently supported for Roman:

      .. table:: Roman Pattern Keyword Names
              :widths: auto
              
              ================  =================  =======================================
              CRDS              ``P_`` ASDF        ``P_`` ROMAN DATAMODELS               
              ================  =================  =======================================
              OPTICAL_ELEMENT   P_OPTICAL_ELEMENT  ROMAN.META.INSTRUMENT.P_OPTICAL_ELEMENT
              ================  =================  =======================================
      
      Each ``P_`` keyword is explicitly defined in CRDS code as well as the CAL code
      data models.  Relative to HST substitutions, the advantage of the ROMAN ``P_``
      keywords is that the pattern values can be defined in arbitrary combinations
      in the reference files instead of CRDS code.  
