.. include:: unicode.rst

ACS Filters and Dispersers
--------------------------

The following tables show the three cameras' 'filters'
properties. The definitions of the columns below are those of the
stsdas.synphot BANDPAR task. These definitions are summarized here. For further
details please see the on-line help on BANDPAR. Here 'INT'
refers to an integral over wavelength, and 'THRU' is the
throughput of the filter at that wavelength. 'LAM' is
wavelength. ::

 Central Wavelength = bandpar.pivwv
    defined as PIVWV = SQRT(INT(THRU * LAM) / INT (THRU / LAM))
 Mean Wavelength = bandpar.avgwv
    defined as AVGWV = INT(THRU * LAM) / INT(THRU)
 Peak Wavelength = bandpar.wpeak
    defined as wavelength at peak throughput (WPEAK)
 FWHM = bandpar.fwhm
    defined as FWHM = SQRT(8 * LOG(2)) * BANDW
 Max Transmission = maximum transmission OF THE FILTER ONLY
    (no other optical components) as measured pre-launch in the lab
 Max Throughput = bandpar.tpeak
    defined as peak bandpass throughput


The Range column describes the total range in wavelength where the
filter throughput (by itself, no other optical components) is larger
than 0.05%. For low-pass filters, the range is open-ended; the table
lists in this case the range as the maximum range listed in the
SYNPHOT/*pysynphot* throughput reference files.

The rightmost column, Fraction, is the fraction of light falling on
the central pixel, assuming the point source PSF is centered on that
pixel as estimated by Tiny Tim PSF simulations (3-gyro mode).

All data in these tables (except for the PSF-related
'Fraction') are generated from the STScI CDBS tables,
which are updated as more accurate information is obtained. The
observer is strongly advised to regenerate these tables from the most
up-to-date data in CDBS if the exact values are critical to planning
observations. The SYNPHOT user's guide (Bushouse, 1998) is the best
guide on how to do this.



HRC Filters
...........

\

======     =======     ======     ======     ======     ======     =========     ========     ========     
Filter     Central     Mean       Peak       FWHM       Range      Trans         Thru         Fraction     
======     =======     ======     ======     ======     ======     =========     ========     ========     
F475W      4775.7      4794.0     5000.2     986.23     1800       0.913701      0.24735      0.17         
F502N      5022.9      5023.0     5005.5     85.867     145        0.7135654     0.19196      0.169        
F550M      5579.9      5582.4     5550.3     389.02     740        0.8770255     0.24687      0.153        
F555W      5356.0      5368.0     5059.8     841.13     1720       0.885         0.24037      0.159        
F606W      5888.0      5926.1     6689.8     1565.5     2570       0.9517956     0.27447      0.143        
F625W      6295.5      6309.2     6479.9     977.51     1720       0.915         0.26496      0.134        
F658N      6583.8      6584.0     6592.0     136.27     180        0.9118735     0.26505      0.128        
F775W      7665.1      7677.5     7320.1     1017.4     1910       0.947         0.23605      0.107        
F850LP     9145.2      9161.6     8859.5     1269.1     >3080      0.976         0.13813      0.086        
F892N      8916.1      8916.4     8915.4     237.98     320        0.9182586     0.13461      0.091        
F220W      2255.4      2264.4     2219.9     441.03     1350       0.361         0.050401     0.175        
F250W      2715.9      2727.4     2520.1     563.76     1980       0.48071       0.061124     0.166        
F330W      3362.7      3367.2     3460.3     409.16     790        0.751         0.10714      0.156        
F344N      3433.7      3433.8     3430.2     64.922     95         0.67994       0.10093      0.156        
F435W      4311.0      4322.0     4760.1     728.95     8780       0.92799       0.22602      0.17         
F660N      6599.1      6599.3     6595.4     175.72     100        0.7178267     0.20719      0.128        
F814W      8115.3      8146.9     7459.5     1656.6     2870       0.991         0.23965      0.099        
POL_UV     6231.7      6607.0     7399.7     4943.9     >18000     1.0           0.088816     0.135        
POL_V      6943.2      7184.0     9206.6     4134.8     >16500     1.0           0.086172     0.121        
PR200L     5650.2      6051.9     6460.4     4830.5     >9392      0.93          0.26908      0.151        
CORON      5472.0      5926.3     6460.4     4926.1     \          0.475         0.13743      0.156        
G800L      7506.4      7594.9     7000.0     2614.3     >6000      0.902         0.22724      0.110        
======     =======     ======     ======     ======     ======     =========     ========     ========     

|

SBC Filters
...........
\

==========     ===========     ========     ========     ========     =========     =========     =========     ============     
**Filter**     **Central**     **Mean**     **Peak**     **FWHM**     **Range**     **Trans**     **Thru**      **Fraction**     
==========     ===========     ========     ========     ========     =========     =========     =========     ============     
F115LP         1406.1          1415.0       1260.2       354.53       >8850         0.92705       0.057976      0.101            
F122M          1273.7          1277.5       1216.0       213.97       1170          0.143         0.0095276     0.078            
F125LP         1437.5          1445.2       1320.0       334.09       >8780         0.91          0.0529        0.108            
F140LP         1527.0          1532.6       1390.1       294.08       >8650         0.89          0.04167       0.125            
F150LP         1610.7          1614.7       1490.0       258.52       >8600         0.86812       0.029992      0.141            
F165LP         1757.9          1760.1       1700.1       203.2        >8500         0.85          0.0090218     0.162            
PR110L         1429.4          1438.1       1320.1       355.49       >8800         0.89444       0.045411      0.106            
PR130L         1438.7          1446.6       1299.9       336.48       >8780         0.89611       0.053365      0.108            
==========     ===========     ========     ========     ========     =========     =========     =========     ============     

|

WFC Filters
............

\

==========     ===========     ========     ========     ========     =========     =========     ========     ============     
**Filter**     **Central**     **Mean**     **Peak**     **FWHM**     **Range**     **Trans**     **Thru**     **Fraction**     
==========     ===========     ========     ========     ========     =========     =========     ========     ============     
F475W          4744.4          4763.0       4999.6       989.27       1800          0.913701      0.3736       0.213            
F502N          5023.0          5023.1       5005.5       68.042       145           0.7135654     0.28985      0.210            
F550M          5581.2          5583.5       5550.4       384.47       740           0.8770255     0.38211      0.216            
F555W          5359.6          5371.8       5499.8       847.79       1720          0.885         0.37093      0.214            
F606W          5917.7          5956.3       6689.8       1583.2       2570          0.9517956     0.46516      0.219            
F625W          6310.5          6324.1       6479.9       978.32       1720          0.915         0.44337      0.22             
F658N          6584.0          6584.4       6591.6       87.487       180           0.9118735     0.44498      0.22             
F775W          7693.0          7705.4       7380.3       1023.4       1910          0.947         0.42868      0.206            
F850LP         9054.8          9071.6       8610.3       1270.3       >3080         0.976         0.24829      0.147            
F892N          8914.9          8915.1       8914.9       171.78       320           0.9182586     0.21473      0.154            
F435W          4317.4          4327.3       4569.9       691.08       8780          0.92799       0.3807       0.217            
F660N          6599.4          6599.5       6595.2       83.666       100           0.7178267     0.34844      0.0.22           
F814W          8059.8          8087.4       7460.2       1541.6       2870          0.991         0.44092      0.197            
POL_UV         6634.5          6874.9       7640.4       4053.7       >1800         1.0           0.16482      0.22             
POL_V          6910.0          7134.4       7209.6       4017.0       >16500        1.0           0.1386       0.22             
G800L          7480.7          7559.1       7199.8       2473.0       >6000         0.902         0.40081      0.210            
==========     ===========     ========     ========     ========     =========     =========     ========     ============ 
  
|

Ramp Filters
............
\

.. Note that |cdelta| |lambda| did not render correctly in all contexts
.. and hence "Range" was substituted in column 3 below

==========     ===========     =========    ==========     
**Filter**     **Central**     **Range**    **Camera**     
==========     ===========     =========    ==========     
FR388N         3710-4050       2%           WFC/HRC        
FR423N         4050-4420       2%           WFC            
FR462N         4420-4820       2%           WFC            
FR656N         6270-6850       2%           WFC/HRC        
FR716N         6850-7470       2%           WFC            
FR782N         7470-8160       2%           WFC            
FR914M         7570-10710      9%           WFC/HRC        
FR853N         8160-8910       2%           WFC            
FR931N         8910-9720       2%           WFC            
FR459M         3810-5370       9%           WFC/HRC        
FR647M         5370-7570       9%           WFC            
FR1016N        9720-10610      2%           WFC            
FR505N         4820-5270       2%           WFC/HRC        
FR551N         5270-5750       2%           WFC            
FR601N         5750-6270       2%           WFC            
==========     ===========     =========    ==========     

Please refer to Bohlin and Tsvetanov
( `ISR ACS 00-05 <http://www.stsci.edu/hst/acs/documents/isrs/isr0005.pdf>`_ ) for details about calculation of peak transmission for
ramp filters.

