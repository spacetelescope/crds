#!/bin/csh -x
#
# 01/13/03 48141  MSwam  original
# 04/20/04 48141  MSwam  e-mail operator log
# 05/12/04 48141  MSwam  e-mail when error exit occurs as well
# 10/20/04 51433  MSwam  change logging and catch stderr from update task
#
#----------------------------------------------------------------------
#
set all_is_well = 0  # exit status for success
set run_failed = 1   # exit status for failure

set ymd_HM = `date '+%y%m%d_%H%M'`
set logname = daily_best_ref.log.${ymd_HM}
\rm $logname
cd ${OUTPATH}
#
echo "+++++++++++++++++++++++++++++++"
echo "+++++++ starting update +++++++"
echo "+++++++++++++++++++++++++++++++"
#
# instrument names must match those in the fullmaster.xml file
set INSTRUMENT_LIST = (${SUPPORTED_INSTR})
while $#INSTRUMENT_LIST
  setenv INSTR $INSTRUMENT_LIST[1]
  date
  echo "processing update ${INSTR}"

  # generate the SQL updates, if any
  #
  update_ref_files.py -i ${INSTR} -o ${INSTR}.sqlout |& tee -a $logname
  if ($status != 0) then
    echo "ERROR: update_files.py FAILED"
    cat $logname | mailx -s "BESTREF: ERROR during New Exposures run" ${OPERATOR_MAIL_LIST}
    exit $run_failed
  endif
  echo " " | tee -a $logname

  # apply SQL updates if any
  #
  set count=`cat ${INSTR}.sqlout | wc -l`
  if ($count > 1) then
    echo "updating database..."
    isql -w132 -S${ARCH_SERVER} -D${ARCH_DB} -i ${INSTR}.sqlout -o tmp$$
    # append result of SQL to log
    cat tmp$$ >> $logname
    \rm tmp$$
    # save SQL for problem inspection
    \mv ${INSTR}.sqlout ${INSTR}.sqlout.${ymd_HM}
  endif
  shift INSTRUMENT_LIST
end
date
#
#
# send logs to operator e-mail list
#
cat $logname | mailx -s "BESTREF: New Exposures run" ${OPERATOR_MAIL_LIST}

exit ${all_is_well}
