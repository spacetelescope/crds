#from crds.hst.lookup import HstRmapSelector
#from crds.selectors import UseAfterSelector
#import crds.log as log
#class AcsBiasfileSelector(HstRmapSelector):
#    '''
#     #   See cdbsquery and reference_file_defs.xml
#
#      # skip these (not used in selection, only for special tests)
#      if (k._field == 'XCORNER' or k._field == 'YCORNER' or
#          k._field == 'CCDCHIP'):
#          continue
#      #
#      # special cases
#      elif k._field == 'NUMROWS':
#        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis2 = OBS_NAXIS2 "
#        continue
#      elif k._field == 'NUMCOLS':
#        querytxt = querytxt + "and acs_row_"+querynum+ ".naxis1 = OBS_NAXIS1 "
#        continue
#      elif k._field == 'LTV1':
#        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv1 = OBS_LTV1 "
#        continue
#      elif k._field == 'LTV2':
#        querytxt = querytxt + "and acs_row_"+querynum+ ".ltv2 = OBS_LTV2 "
#        continue
#      # only apply this case for exposures before SM4
#      elif k._field == 'CCDAMP' and not beyond_SM4:
#        #
#        # convert amp A reads to AD if size is more than half a chip
#        if (aSource._keywords["CCDAMP"][0] == "A" and
#            aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
#            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp A "+
#                                  "to AD for NUMCOLS = "+
#                                  str(aSource._keywords["NUMCOLS"][0]))
#            aSource._keywords["CCDAMP"][0] = "AD"
#        #
#        # convert amp B reads to BC if size is more than half a chip
#        elif (aSource._keywords["CCDAMP"][0] == "B" and
#              aSource._keywords["NUMCOLS"][0] > ACS_HALF_CHIP_COLS):
#            opusutil.PrintMsg("I","acs_bias_file_selection: exposure is pre-SM4, converting amp B "+
#                                  "to BC for NUMCOLS = "+
#                                  str(aSource._keywords["NUMCOLS"][0]))
#            aSource._keywords["CCDAMP"][0] = "BC"
#      #
#      # apply the file selection field
#      # (first as a string, but if that fails, as a number converted to string,
#      #  since numbers are not quoted but string are)
#      try:
#        querytxt = (querytxt + "and acs_row_"+querynum+"." +
#                 string.lower(k._field) + " = '" +
#                 aSource._keywords[k._field][0] + "' ")
#      except TypeError:
#        querytxt = (querytxt + "and acs_row_"+querynum+"." +
#                 string.lower(k._field) + " = " +
#                 str(aSource._keywords[k._field][0]) + " ")
#    #
#    return querytxt
#    '''
#
#class AcsPfltfileSelector(HstRmapSelector):
#    '''
#
#    <REFFILE>
#    <REFFILE_TYPE> PFL </REFFILE_TYPE>
#    <REFFILE_KEYWORD> PFLTFILE </REFFILE_KEYWORD>
#    <REFFILE_FORMAT> IMAGE </REFFILE_FORMAT>
#    <REFFILE_REQUIRED> YES </REFFILE_REQUIRED>
#    <REFFILE_SWITCH> FLATCORR </REFFILE_SWITCH>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> DETECTOR </FILE_SELECTION_FIELD>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> CCDAMP </FILE_SELECTION_FIELD>
#      <FILE_SELECTION_TEST> (aSource._keywords['DETECTOR'][0] != 'SBC') </FILE_SELECTION_TEST>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> FILTER1 </FILE_SELECTION_FIELD>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> FILTER2 </FILE_SELECTION_FIELD>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> OBSTYPE </FILE_SELECTION_FIELD>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> FW1OFFST </FILE_SELECTION_FIELD>
#      <FILE_SELECTION_TEST> (aSource._keywords['FW1OFFST'][0] == -1 or aSource._keywords['FW1OFFST'][0] == 1) </FILE_SELECTION_TEST>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> FW2OFFST </FILE_SELECTION_FIELD>
#      <FILE_SELECTION_TEST> (aSource._keywords['FW2OFFST'][0] == -1 or aSource._keywords['FW2OFFST'][0] == 1) </FILE_SELECTION_TEST>
#    </FILE_SELECTION>
#    <FILE_SELECTION>
#      <FILE_SELECTION_FIELD> FWSOFFST </FILE_SELECTION_FIELD>
#      <FILE_SELECTION_TEST> (aSource._keywords['FWSOFFST'][0] == -1 or aSource._keywords['FWSOFFST'][0] == 1) </FILE_SELECTION_TEST>
#    </FILE_SELECTION>
#    <RESTRICTION>
#      <RESTRICTION_TEST> (aSource._keywords['OBSTYPE'][0] != 'INTERNAL') </RESTRICTION_TEST>
#    </RESTRICTION>
#  </REFFILE>
#    '''
#    def ignored_keys(self, header):
#        ignored = []
#        for key in ["FW1OFFST","FW2OFFST","FWSOFFST"]:
#            if (key in header) and (header[key] not in ["1.0", "-1.0", 1.0, -1.0]):
#                ignored.append(key)
#        return ignored
#
## 'DETECTOR', '*CCDAMP', 'FILTER1', '*FILTER2', '*OBSTYPE', '*FW1OFFST', '*FW2OFFST', '*FWSOFFST'
#def fix_fw_offset(key):
#    new_key = list(key[:-3])
#    for offst in key[-3:]:
#        if offst == "0.0":
#            offst = "*"
#        new_key.append(offst)
#    return tuple(new_key)
#
#def acs_pfltfile_filter(kmap):
#    items = kmap.items()
#    new_kmap = {}
#    for key, filemaps in items:
#        new_key = fix_fw_offset(key)
#        if new_key not in new_kmap:
#            new_kmap[new_key] = []
#        new_kmap[new_key].extend(filemaps)
#    return new_kmap, []

