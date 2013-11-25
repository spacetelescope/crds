#!/bin/csh -x
#
# 04/12/04 48141  MSwam  changed from original to new Python-based BESTREF
# 04/20/04 48141  MSwam  e-mail of logfile
# 05/12/04 48141  MSwam  add e-mail of failed logfile as well
# 10/20/04 51433  MSwam  catch stderr messages from new_ref_files as well
# 06/16/10 64432  MSwam  reworked a query so MS SQLServer double-quote behavior
#                          can be dealt with, but then realized the feature
#                          had been broken for a long time, so just turned it
#                          off
# 09/08/10 64432  MSwam  replace !=NULL with is not NULL
#----------------------------------------------------------------------
set all_is_well = 0  # exit status for success
set run_failed = 1   # exit status for failure

#
# database updates are performed in chunks to ease replication burden

set ymd_HM = `date '+%y%m%d_%H%M'`
set logname = new_reffiles.log.${ymd_HM}
\rm $logname
cd ${OUTPATH}
#
echo "+++++++++++++++++++++++++++++++"
echo "+++++++++ starting new ++++++++"
echo "+++++++++++++++++++++++++++++++"
date

# The timestmp update will only occur
#   for new files that have been successfully loaded by OPUS.
#   This ensures the pipeline has the files before BESTREF
#   starts recommending them.
#
#  instrument names must match those used in naming CDBS db tables
set INSTRUMENT_LIST = (${SUPPORTED_INSTR})
while $#INSTRUMENT_LIST
  setenv CURRENT_INSTRUMENT $INSTRUMENT_LIST[1]
  date
  echo "setting timestmp for ${CURRENT_INSTRUMENT}"
  isql -S${CDBS_SERVER} -D${CDBS_DB} << eof
UPDATE new_cal_files set timestmp = getdate() FROM
new_cal_files n, ${CURRENT_INSTRUMENT}_file f WHERE
n.file_name = f.file_name and
n.expansion_number = f.expansion_number and
f.opus_load_date is not NULL
go
exit
eof
  shift INSTRUMENT_LIST
end

echo "processing new"
\rm new_files.sqlout
#
# new_files handles ALL instruments at once
# generate the SQL updates
#
new_ref_files.py -o new_files.sqlout -l ${UPDATE_LIMIT} |& tee -a $logname
if ($status != 0) then
  echo "ERROR: new_files.py FAILED."
  cat $logname new_files.sqlout | mailx -s "BESTREF: ERROR during New Reference file run" ${OPERATOR_MAIL_LIST}
  exit $run_failed
endif

# apply SQL updates, if any
set count=`cat new_files.sqlout | wc -l`
if ($count > 1) then
  isql -S${ARCH_SERVER} -e -D${ARCH_DB} -i new_files.sqlout -o tmp$$
  # save for problem checking
  cat tmp$$ >> $logname
  \mv tmp$$ new_files.sqlout.${ymd_HM}
endif

#=====================================================
#(CURRENTLY TURNED OFF, since no one seemed to care when it was broken)
# generate changes for mailing to SI teams 
#
#set INSTRUMENT_LIST = (${SUPPORTED_INSTR})
#while $#INSTRUMENT_LIST
# set INSTR=$INSTRUMENT_LIST[1]
# set UP_INSTR=`echo ${INSTR} | tr '[a-z]' '[A-Z]'`
# # write SQL to a file, since SQL Server can't deal with double-quoted strings
# # and csh won't expand env vars inside a single-quoted string
# #
# echo "select distinct file_name from new_cal_files where instrument = '""${UP_INSTR}""'" > sqlTemp$$
# echo "go" >> sqlTemp$$
# #
# isql -S${CDBS_SERVER} -D${CDBS_DB} -i sqlTemp$$ > ${INSTR}.out
# shift INSTRUMENT_LIST
#end
#rm sqlTemp$$
#
#
# could report changes to SI mailing list (this was broken for a long time
#   and no one cared, so it was turned off)
#
#if !(-z stis.out) then
#  mailx -s "The following STIS reference files have been used in the latest best ref run" ${STIS_MAIL_LIST} < stis.out
#  \rm stis.out
#endif
#=====================================================

# move off tagged records into the history table
#
isql -S${CDBS_SERVER} -D${CDBS_DB} -e -o tmp$$ << EOF
insert into new_cal_files_history 
select instrument,file_name,expansion_number,getdate(),timestmp 
from new_cal_files where timestmp is not null
go
select * from new_cal_files
go
delete from new_cal_files where timestmp is not null
go
exit
EOF
\cat tmp$$ >> $logname
\rm tmp$$
#
# send logs to operator e-mail list, if any new files were processed
#
if ($count > 1) then
  \cat $logname | mailx -s "BESTREF: New Reference file run" ${OPERATOR_MAIL_LIST}
endif

exit $all_is_well
