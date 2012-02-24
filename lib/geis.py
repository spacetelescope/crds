"""This module supports reading HST GEIS file headers.

>>> is_geis_header("foo.r0h")
True
>>> is_geis_header("bar.fits")
False

>>> header = get_geis_header(cStringIO.StringIO(_TEST_DATA))
>>> pprint.pprint(header)
    {'ATODGAIN': '0.',
     'BITPIX': '16',
     'DATATYPE': 'INTEGER*2',
     'DESCRIP': 'STATIC MASK - INCLUDES CHARGE TRANSFER TRAPS',
     'FILETYPE': 'MSK',
     'FILTER1': '0',
     'FILTER2': '0',
     'FILTNAM1': '',
     'FILTNAM2': '',
     'GCOUNT': '4',
     'GROUPS': 'T',
     'HISTORY': ['This file was edited by Michael S. Wiggs, August 1995',
                 '',
                 'e2112084u.r0h was edited to include values of 256, which correspond'],
     'INSTRUME': 'WFPC2',
     'KSPOTS': 'OFF',
     'NAXIS': '1',
     'NAXIS1': '800',
     'PCOUNT': '38',
     'PDTYPE1': 'REAL*8',
     'PDTYPE2': 'REAL*8',
     'PEDIGREE': 'INFLIGHT 01/01/1994 - 15/05/1995',
     'PSIZE': '1760',
     'PSIZE1': '64',
     'PSIZE2': '64',
     'PTYPE1': 'CRVAL1',
     'PTYPE2': 'CRVAL2',
     'ROOTNAME': 'F8213081U',
     'SHUTTER': '',
     'SIMPLE': 'F',
     'UBAY3TMP': '0.',
     'UCH1CJTM': '0.',
     'UCH2CJTM': '0.',
     'UCH3CJTM': '0.',
     'UCH4CJTM': '0.'}
"""

import os.path
import re
import sys
import cStringIO
import pprint

_TEST_DATA = """
SIMPLE  =                    F /
                                                                              
BITPIX  =                   16 /                                                
DATATYPE= 'INTEGER*2'          /                                                
NAXIS   =                    1 /                                                
NAXIS1  =                  800 /                                                
GROUPS  =                    T /                                                
GCOUNT  =                    4 /                                                
PCOUNT  =                   38 /
PSIZE   =                 1760 /                                                
PTYPE1  = 'CRVAL1  '           /right ascension of reference pixel              
PDTYPE1 = 'REAL*8  '           /                                                
PSIZE1  =                   64 /                                                
PTYPE2  = 'CRVAL2  '           /declination of reference pixel                  
PDTYPE2 = 'REAL*8  '           /                                                
PSIZE2  =                   64 /                                                
                                                                                
                               / GROUP PARAMETERS: OSS                          
                                                                                
                                                                                
                               / GROUP PARAMETERS: PODPS                        
                                                                                                                                                                
INSTRUME= 'WFPC2   '           / instrument in use                              
ROOTNAME= 'F8213081U'          / rootname of the observation set                
FILETYPE= 'MSK     '           / shp, ext, edq, sdq, sci                        
                                                                                
                               / SCIENCE INSTRUMENT CONFIGURATION               
                                                                                
FILTNAM1= '        '           / first filter name                              
FILTNAM2= '        '           / second filter name                             
FILTER1 =                    0 / first filter number (0-48)                     
FILTER2 =                    0 / second filter number (0-48)                    
                                                                                
UCH1CJTM=                   0. / TEC cold junction #1 temperature (Celcius)     
UCH2CJTM=                   0. / TEC cold junction #2 temperature (Celcius)     
UCH3CJTM=                   0. / TEC cold junction #3 temperature (Celcius)     
UCH4CJTM=                   0. / TEC cold junction #4 temperature (Celcius)     
UBAY3TMP=                   0. / Bay 3 A1 temperature (Celcius)                 
KSPOTS  = 'OFF     '           / Status of Kelsall spot lamps: ON, OFF          
SHUTTER = '        '           / Shutter in place during preflash or IFLAT (A,B)
ATODGAIN=                   0. /                                                
                                                                                
                               / RSDP CONTROL KEYWORDS                          
                                                                                
PEDIGREE= 'INFLIGHT 01/01/1994 - 15/05/1995'                                    
DESCRIP = 'STATIC MASK - INCLUDES CHARGE TRANSFER TRAPS'                        
HISTORY This file was edited by Michael S. Wiggs, August 1995                   
HISTORY                                                                         
HISTORY e2112084u.r0h was edited to include values of 256, which correspond     
END                                                                             
"""

def is_geis_header(name):
    name = os.path.basename(name)
    return bool(re.match(r"\w+\.r\dh", name))

def get_geis_header(name, needed_keys=[]):
    """Return the `needed_keys` from GEIS file at `name`."""

    lines = open(name) if isinstance(name, str) else name

    header = {}
    history = []

    for line in lines:

        # Drop comment
        if len(line) >= 32 and line[31] == "/":
            line = line[:31]
            
        if line.startswith("HISTORY"):
            history.append(line[len("HISTORY"):].strip())
            continue

        words = [x.strip() for x in line.split("=")]

        if len(words) < 2:
            continue
        
        key = words[0]
        
        # Skip over unneeded keys            
        if needed_keys and key not in needed_keys:
            continue
        
        # Recombine value / comment portion
        value = "=".join(words[1:])

        # Remove quotes from strings        
        value = value.strip()
        if value and value[0] == "'" and value[-1] == "'":
            value = value[1:-1].strip()

        # Assign value,  supporting list of values for HISTORY
        header[key] = value
        
    if not needed_keys or "HISTORY" in needed_keys:
        header["HISTORY"] = history
    
    return header

def test():
    import doctest, geis
    return doctest.testmod(geis)

if __name__ == "__main__":
    print test()

