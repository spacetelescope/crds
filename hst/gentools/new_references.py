"""This script checks the HST reference file database for new files which
can be used for test exercises with CRDS to pace new CDBS submissions.  It
prints out the reference files archived after the specified date which are

"""

import sys

import crds
from crds import hst, timestamp, log, client

import cdbs_db

def print_new_references(context="hst.pmap", date="1990-01-01", time="00:00", 
                         check_existing=True):

    r = cdbs_db.get_reffile_ops()

    if check_existing:
        client.set_crds_server("http://etcbrady.stsci.edu:4997")
        existing_references = client.get_reference_names(context)

    start_date = timestamp.reformat_date(date + " " + time)

    for instrument in hst.INSTRUMENTS:

        if instrument == "nicmos":
            instrument = "nic"      # wheee!

        already_checked = set()

        files = r.make_dicts(instrument + "_file")
        for f in files:

            adate = f["archive_date"]
            fname = f["file_name"]

            if fname in already_checked:
                continue
            else:
                already_checked.add(fname)

            log.verbose("Checking", repr(fname), "archived on", repr(adate), verbosity=60)

            if adate == "none":
                log.verbose("Skipping", repr(fname),"no ARCHIVE.", verbosity=60)
                continue

            try:
                fdate = timestamp.reformat_date(adate)
            except:
                log.error("Time format error for", repr(fname), "time", repr(adate))
                continue
            
            if fdate < start_date:
                log.verbose("Skipping",repr(fname),"archived prior to start date.", verbosity=60)
                continue
            if f["opus_flag"].upper()[0] != "Y":
                log.verbose("Skipping", repr(fname),"no OPUS.")
                continue
            if f["reject_flag"].upper()[0] == "Y":
                log.verbose("Skipping", repr(fname),"rejected.")
                continue
            if check_existing and fname in existing_references:
                log.verbose("Skipping",repr(fname),"already known to context.")
                continue

            print fname, fdate

if __name__ == "__main__":
    if "--verbose" in sys.argv:
        sys.argv.remove("--verbose")
        log.set_verbose(True)
        
    check_existing = False
    if "--check-existing" in sys.argv:
        sys.argv.remove("--check-existing")
        check_existing = True

    if len(sys.argv) < 2:
        sys.stderr.write("usage: " + sys.argv[0] + " <context> [YYYY-MM-DD [HH:MM:SS.XX]]\n")
        sys.exit(-1)

    print_new_references(*tuple(sys.argv[1:]), check_existing=check_existing)

