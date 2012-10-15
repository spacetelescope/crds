import sys

from crds import log, utils, timestamp

# ===========================================================================    

ACS_HALF_CHIP_COLS = 2048         #used in custom bias selection algorithm

SM4 = timestamp.reformat_date("2009-05-14 00:00")
# date beyond which an exposure was
# taken in the SM4 configuration
# (day 2009.134 = May 14 2009,
#  after HST was captured by 
#  the shuttle during SM4, and
#  pre-SM4 exposures had ceased)

def _precondition_header_biasfile(header_in):
    """Mutate the incoming dataset header based upon hard coded rules
    and the header's contents.   This is an alternative to generating
    an equivalent and bulkier rmap.
    """
    header = dict(header_in)
    exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
    if (exptime < SM4):
        if "APERTURE" not in header or header["APERTURE"] == "UNDEFINED":
            header["APERTURE"] = "N/A"
    return header     # XXXXXX RETURN NOW !!!!
    
    # Theoretical code copying cdbsquery.py just introduces mismatches...
    try:
        numcols = float(header["NUMCOLS"])
    except ValueError:
        log.verbose("acs_biasfile_selection: bad NUMCOLS.")
        sys.exc_clear()
    else:
        # if pre-SM4 and NUMCOLS > HALF_CHIP
        exptime = timestamp.reformat_date(header["DATE-OBS"] + " " + header["TIME-OBS"])
        if (exptime < SM4):
            if numcols > ACS_HALF_CHIP_COLS:
                if header["CCDAMP"] in ["A","D"]: 
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp A or D "+
                                "to AD for NUMCOLS = "+ header["NUMCOLS"])
                    header["CCDAMP"] = "AD"
                elif header["CCDAMP"] in ["B","C"]:  
                    log.verbose("acs_bias_file_selection: exposure is pre-SM4, converting amp B or C "+
                                "to BC for NUMCOLS = "+ header["NUMCOLS"])
                    header["CCDAMP"] = "BC"
    if header['DETECTOR'] == "WFC" and \
        header['XCORNER'] == "0.0" and header['YCORNER'] == "0.0":
        log.verbose("acs_biasfile_selection: precondition_header halving NUMROWS")
        try:
            numrows = float(header["NUMROWS"]) / 2
        except ValueError:
            log.verbose("acs_biasfile_selection: bad NUMROWS.")
            sys.exc_clear()
        else:
            header["NUMROWS"] = utils.condition_value(str(numrows)) 

    return header

def precondition_header(rmap, header):
    header = dict(header)
    if rmap.filekind == "biasfile":
        return _precondition_header_biasfile(header)
    else:
        return header
    
# ===========================================================================    


def _fallback_biasfile(header_in):
    header = _precondition_header_biasfile(header_in)
    log.verbose("No matching BIAS file found for",
               "NUMCOLS=" + repr(header['NUMCOLS']),
               "NUMROWS=" + repr(header['NUMROWS']),
               "LTV1=" + repr(header['LTV1']),
               "LTV2=" + repr(header['LTV2']))
    log.verbose("Trying full-frame default search")
    if header['DETECTOR'] == "WFC":
        header["NUMCOLS"] = "4144.0"
        header["NUMROWS"] = "2068.0"
        header["LTV1"] = "24.0"
        header["LTV2"] = "0.0"
    else:
        header["NUMCOLS"] = "1062.0"
        header["NUMROWS"] = "1044.0"
        header["LTV1"] = "19.0"
        if header['CCDAMP'] in ["C","D"]:
            header["LTV2"] = "0.0"
        else: # assuming HRC with CCDAMP = A or B
            header["LTV2"] = "20.0"
    return header

def fallback_header(rmap, header):
    if rmap.filekind == "biasfile":
        # log.info("x", end="",sep="")
        return _fallback_biasfile(header)
    else:
        None

# =============================================================================================

header_additions = [   # dictionary items (ordered)
]

def acs_biasfile_filter(kmap):
    """APERTURE was added late as a matching parameter and so many existing references
    have an APERTURE value of '' in CDBS.   Where it's relevant,  it's actually defined.
    Here we change '' to N/A to make CRDS ignore it when it doesn't matter;  resulting matches
    will be "weaker" than matches with a real APERTURE value.
    """
    log.info("Hacking ACS biasfile  APERTURE macros.  Changing APERTURE='' to APERTURE='N/A'")
    for match, value in kmap.items():
        if match[3] == '':
            new = list(match)
            new[3] = 'N/A'
            kmap[tuple(new)] = value
            del kmap[match]
#     kmap[('UVIS', 'G280_AMPS', 1.5, 1.0, 1.0, 'G280-REF', 'T')] = \
#       [rmap.Filemap(date='1990-01-01 00:00:00', file='t6i1733ei_bia.fits',
#               comment='Placeholder file. All values set to zero.--------------------------, 12047, Jun 18 2009 05:36PM')]
    return kmap, header_additions

'''
  def acs_biasfile(self, thereffile, aSource):
    # the query templates
    # (no need to define these outside, like those for the generic case, since
    #  this routine is only called once per dataset)
    query_template_a = (
       "SELECT max(acs_file_1.file_name) "+
       "FROM acs_file acs_file_1, acs_row acs_row_1 "+
       "WHERE acs_file_1.useafter_date = "+
           "(SELECT max(acs_file_2.useafter_date) "+
           "FROM acs_file acs_file_2, acs_row acs_row_2 "+
               "WHERE acs_file_2.reference_file_type = 'BIA' "+
               "and acs_file_2.useafter_date <= 'EXPOSURE_START' "+
               "and acs_file_2.reject_flag = 'N' "+
               "and acs_file_2.opus_flag = 'Y' "+
               "and acs_file_2.archive_date is not null "+
               "and acs_file_2.opus_load_date is not null "+
               "and acs_file_2.file_name =acs_row_2.file_name "+
               "and acs_file_2.expansion_number = acs_row_2.expansion_number ")
    #
    query_template_b = (
           ") and acs_file_1.reference_file_type = 'BIA' "+
       "and acs_file_1.reject_flag = 'N' "+
       "and acs_file_1.opus_flag = 'Y' "+
       "and acs_file_1.archive_date is not null "+
       "and acs_file_1.opus_load_date is not null "+
       "and acs_file_1.file_name =acs_row_1.file_name "+
       "and acs_file_1.expansion_number = acs_row_1.expansion_number ")

    querytxt = query_template_a

    # fill the exposure start time, after converting keyword value
    # to datetime format from source format
    #
    exposure_start, beyond_SM4 = self.find_exposure_start(aSource)
    querytxt = string.replace(querytxt,"EXPOSURE_START", exposure_start)                         
    # adjust naxis2 for WFC full-array images
    try:
      obs_naxis2 = aSource._keywords['NUMROWS'][0]
      if (aSource._keywords['DETECTOR'][0] == "WFC" and
          aSource._keywords['XCORNER'][0] == 0 and
          aSource._keywords['YCORNER'][0] == 0) :
        #
        # image is half of the specific size (2 chips)
        obs_naxis2 = obs_naxis2 / 2
    except KeyError:
      # missing key parameters
      opusutil.PrintMsg("E","Key parameters missing for acs_biasfile")
      raise ZeroRowsFound, "missing one of NUMROWS, DETECTOR, XCORNER, YCORNER"

    # add the file selection fields (row_2)
    querytxt = querytxt + self.acs_bias_file_selection("2", thereffile, aSource,
                                                       beyond_SM4)

    # add second template
    querytxt = querytxt + query_template_b
    
    # add the file selection fields again (row_1)
    querytxt = querytxt + self.acs_bias_file_selection("1", thereffile, aSource,
                                                       beyond_SM4)
    
    # replace the place-holders in the query with the real selection values
    query1 = string.replace(querytxt,"OBS_NAXIS1", 
                                       str(aSource._keywords['NUMCOLS'][0]))
    query1 = string.replace(query1,"OBS_NAXIS2", str(obs_naxis2))
    query1 = string.replace(query1,"OBS_LTV1",
                                       str(aSource._keywords['LTV1'][0]))
    query1 = string.replace(query1,"OBS_LTV2",
                                       str(aSource._keywords['LTV2'][0]))

    # replace any None values with null
    query1 = string.replace(query1, "None", "null")                         

    # get results in a list of lists
    result = [[]]
    self.zombie_select(query1, result)
    if len(result) == 0 or result[0][0] == None:
      #
      # no matching CDBS record found for inital search, try full-frame search
      opusutil.PrintMsg("D","No matching BIAS file found for "+
                            "naxis1="+str(aSource._keywords['NUMCOLS'][0])+
                            " naxis2="+str(obs_naxis2)+
                            " ltv1="+str(aSource._keywords['LTV1'][0])+
                            " ltv2="+str(aSource._keywords['LTV2'][0]))
      opusutil.PrintMsg("D","Trying full-frame default search")
      #
      # replace the place-holders with full-frame selection values
      if aSource._keywords['DETECTOR'][0] == "WFC":
        obs_naxis1 = "4144"
        obs_naxis2 = "2068"
        obs_ltv1 = "24.0"
        obs_ltv2 = "0.0"
      else:
        obs_naxis1 = "1062"
        obs_naxis2 = "1044"
        obs_ltv1 = "19.0"
        if (aSource._keywords['CCDAMP'][0] == "C" or
            aSource._keywords['CCDAMP'][0] == "D"):
          obs_ltv2 = "0.0"
        else: # assuming HRC with CCDAMP = A or B
          obs_ltv2 = "20.0"
      query2 = string.replace(querytxt,"OBS_NAXIS1", obs_naxis1)
      query2 = string.replace(query2,"OBS_NAXIS2", obs_naxis2)
      query2 = string.replace(query2,"OBS_LTV1", obs_ltv1)
      query2 = string.replace(query2,"OBS_LTV2", obs_ltv2)
      #
      # get results in a list of lists
      result = [[]]
      self.zombie_select(query2, result)
      if len(result) == 0 or result[0][0] == None:
        #
        # no matching CDBS record found
        opusutil.PrintMsg("E","No full-frame default BIAS found either.")
        raise ZeroRowsFound, query2
    #
    # return the first filename found
    return result[0][0]
    
    
  def acs_bias_file_selection(self, querynum, thereffile, aSource, beyond_SM4):
    querytxt = ""
    #
    # add the file selection fields
    for k in thereffile._file_selections:
      if k._restrictions:
        # see if the restriction allows this file selection field
        opusutil.PrintMsg("D",'found a file select restricted: '+
                               k._restrictions)
        if (not eval(k._restrictions)):
          opusutil.PrintMsg("D","File_selection on "+k._field+
                                " restricted away")
          continue
      #
      # skip these (not used in selection, only for special tests)
      if (k._field == 'XCORNER' or k._field == 'YCORNER' or
          k._field == 'CCDCHIP'):
          continue
      #
      # special cases
      elif k._field == 'NUMROWS':
        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis2 = OBS_NAXIS2 "
        continue
      elif k._field == 'NUMCOLS':
        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis1 = OBS_NAXIS1 "
        continue
      elif k._field == 'LTV1':
        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv1 = OBS_LTV1 "
        continue
      elif k._field == 'LTV2':
        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv2 = OBS_LTV2 "
        continue
      # only apply this case for exposures before SM4
      elif k._field == 'CCDAMP' and not beyond_SM4:
        #
        # convert amp A or D reads to AD if size is more than half a chip
        if ((aSource._keywords["CCDAMP"][0] == "A" or
             aSource._keywords["CCDAMP"][0] == "D") and
            aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp A or D "+
                                  "to AD for NUMCOLS = "+
                                  str(aSource._keywords["NUMCOLS"][0]))
            aSource._keywords["CCDAMP"][0] = "AD"
        #
        # convert amp B reads to BC if size is more than half a chip
        elif ((aSource._keywords["CCDAMP"][0] == "B" or
               aSource._keywords["CCDAMP"][0] == "C") and
              aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp B or C"+
                                  "to BC for NUMCOLS = "+
                                  str(aSource._keywords["NUMCOLS"][0]))
            aSource._keywords["CCDAMP"][0] = "BC"
      #
      # apply the file selection field
      # (first as a string, but if that fails, as a number converted to string,
      #  since numbers are not quoted but string are)
      try:
        querytxt = (querytxt + "and acs_row_"+querynum+"." +
                 string.lower(k._field) + " = '" + 
                 aSource._keywords[k._field][0] + "' ")
      except TypeError:
        querytxt = (querytxt + "and acs_row_"+querynum+"." +
                 string.lower(k._field) + " = " + 
                 str(aSource._keywords[k._field][0]) + " ")
    #
    return querytxt

'''
