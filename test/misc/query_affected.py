import sys
import os.path

from crds.core import log, utils, config, timestamp, cmdline
from crds.client import api

class QueryAffectedDatasetsScript(cmdline.Script):

    description = """
query_affected_datasets (QAD) queries the CRDS server for datasets affected by the specified
CONTEXT(s), history INDICES, or DATES.  QAD relies on pre-computed results on the server,
so QAD queries are only valid for historical context transitions from the context history.
When no history interval is specified,  QAD uses the last processed context as the starting
point,  and the end of the current history as the stopping point.

Before going too far, a couple of points are in order:

    1. QueryAffectedDatasetsScript is intended to be sub-classed.   By default it just prints dataset
    IDs on STDOUT as well as log and affected datasets computation output to STDERR.   Override the
    use_affected() and use_all_ids() methods to do something custom with the affected dataset IDs,
    either switch-by-switch, or potentially multiple contexts at once, respectively.   Override the
    log_affected() or log_all_ids() methods to customize most logging.   QAD provides basic interaction
    with the context history, affected datasets service, recording state, and error handling.

    2. crds.bestrefs can be used to compute the datasets affected by arbitrary context transitions
    when run locally.   The computation can require minutes to hours depending on number of instruments,
    types, datasets, and tables potentially affected.    For this, the --affected-datasets switch
    configures crds.bestrefs to perform an affected datasets computation using the bundle of standard
    options run on the CRDS servers.

Due to processing order on the server, new contexts appear in the context history as operational
before the datasets affected have been computed.   This framework helps resolve that race condition
and provides options for handling affected datasets computations which contained errors.

To support interactive experimentation, QAD supports listing the context history:

    % query_affected_datasets --list
    (0, '2013-07-02 15:44:53', 'hst.pmap', 'set by system')
    (1, '2013-09-10 18:23:06', 'hst_0003.pmap', 'Updated hst.pmap with new references (known to reffile_ops_rep on harpo) up to 09-10-2013')
    ...
    (85, '2014-09-23 16:48:17', 'hst_0287.pmap', 'Delivery of new WFC3 darks.')
    (86, '2014-10-13 11:26:40', 'hst_0288.pmap', 'Delivery of a new ACS WFC1-1K bias.')
    (87, '2014-10-14 09:34:29', 'hst_0289.pmap', 'Delivery of a new COS FUV BPIXTAB.')

See also the -x and -y parameters below for customizing interactive query ranges.

With no history range specified, QAD selects the last history item processed as the starting point
and the end of the current history as the stopping point.  Normally there's nothing new to report,
the last thing processed was the end of the history and nothing has changed on the server.

    % query_affected_datasets
    CRDS - INFO - No new results available.
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 1 infos

Following a context change,  by default QAD will notice a difference between the last saved context
and the new last context in the history.  QAD is designed to be sub-classed but by default prints log
information and recorded affected datasets output to STDERR.   It prints affected dataset IDs to STDOUT.
Run periodically,  QAD will typically see at most a single context switch.

    % query_affected_datasets > ids
    CRDS - INFO - Fetching effects for (96, '2014-11-25 15:48:40', 'hst_0300.pmap', 'Delivery of a new COS HVTAB for association LCIX02080.')
    ####################################################################################################
    --------------------------------------------------------------------------------------------------------------
    CRDS hst ops datasets affected hst_0299.pmap --> hst_0300.pmap on 2014-11-25-15:50:09
    --------------------------------------------------------------------------------------------------------------
    CRDS - INFO - [2014-11-25 15:50:12,563]  Mapping differences from 'hst_0299.pmap' --> 'hst_0300.pmap' affect:
     {'cos': ['hvtab']}
    CRDS - INFO - [2014-11-25 15:50:12,731]  Possibly affected --datasets-since dates determined by 'hst_0299.pmap' --> 'hst_0300.pmap' are:
     {'cos': '2009-05-11 00:00:00'}
    CRDS - INFO - [2014-11-25 15:50:12,731]  Computing bestrefs for db datasets for ['cos']
    CRDS - INFO - [2014-11-25 15:50:12,731]  Dumping dataset parameters for 'cos' from CRDS server at 'https://hst-crds.stsci.edu' since '2009-05-11 00:00:00'
    CRDS - INFO - [2014-11-25 15:50:16,457]  Downloaded  19592 dataset ids for 'cos' since '2009-05-11 00:00:00'
    CRDS - INFO - [2014-11-25 15:51:16,293]  Updated exposure counts:
     {'COS': {'hvtab': 13696}}
    CRDS - INFO - [2014-11-25 15:51:16,309]  Affected products = 9494
    CRDS - INFO - [2014-11-25 15:51:16,319]  Unique error types: 0
    CRDS - INFO - [2014-11-25 15:51:16,319]  STARTED 2014-11-25 15:50:10.67
    CRDS - INFO - [2014-11-25 15:51:16,319]  STOPPED 2014-11-25 15:51:16.31
    CRDS - INFO - [2014-11-25 15:51:16,319]  ELAPSED 0:01:05.64
    CRDS - INFO - [2014-11-25 15:51:16,319]  19.59 K datasets at 298.47  datasets-per-second
    CRDS - INFO - [2014-11-25 15:51:16,319]  0 errors
    CRDS - INFO - [2014-11-25 15:51:16,319]  0 warnings
    CRDS - INFO - [2014-11-25 15:51:16,319]  12 infos
    --------------------------------------------------------------------------------------------------------------
    OK: CRDS hst ops datasets affected hst_0299.pmap --> hst_0300.pmap on 2014-11-25-15:50:09 : 9494 affected
    --------------------------------------------------------------------------------------------------------------
    ####################################################################################################
    CRDS - INFO - Contributing context switches = 1
    CRDS - INFO - Total products affected = 9494
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 3 infos

    % cat ids
    i9zf01010
    i9zf02010
    i9zf03010
    i9zf04010
    i9zf05010
    ...

STDERR output from multiple context switches is delimited by ########## lines.

For the sake of custom queries,  QAD supports --starting-context (-x) and --stopping-context (-y) parameters to define the
history starting and stopping points.  -x and -y can be specified as CONTEXTS, HISTORY INDICES, or DATES.

    % query_affected_datasets -x 92 -y 94 > ids
    CRDS - INFO - Fetching effects for (92, '2014-11-05 13:53:15', 'hst_0296.pmap', 'Delivery of new ACS bias, dark, and cte_corrected dark reference files.')
    CRDS - INFO - Fetching effects for (93, '2014-11-10 13:11:02', 'hst_0297.pmap', 'The WFC3 Team delivered 3 new dark reference files.')
    ####################################################################################################
    --------------------------------------------------------------------------------------------------------------
    CRDS hst ops datasets affected hst_0295.pmap --> hst_0296.pmap on 2014-11-05-13:55:08
    --------------------------------------------------------------------------------------------------------------
    CRDS - INFO - [2014-11-05 13:55:12,922]  Mapping differences from 'hst_0295.pmap' --> 'hst_0296.pmap' affect:
     {'acs': ['biasfile', 'drkcfile', 'darkfile']}
    CRDS - INFO - [2014-11-05 13:55:13,576]  Possibly affected --datasets-since dates determined by 'hst_0295.pmap' --> 'hst_0296.pmap' are:
     {'acs': '2014-08-26 09:55:53'}
    CRDS - INFO - [2014-11-05 13:55:13,576]  Computing bestrefs for db datasets for ['acs']
    CRDS - INFO - [2014-11-05 13:55:13,576]  Dumping dataset parameters for 'acs' from CRDS server at 'https://hst-crds.stsci.edu' since '2014-08-26 09:55:53'
    CRDS - INFO - [2014-11-05 13:55:39,323]  Downloaded  1431 dataset ids for 'acs' since '2014-08-26 09:55:53'
    CRDS - INFO - [2014-11-05 13:55:52,999]  Updated exposure counts:
     {'ACS': {'biasfile': 1374, 'darkfile': 1386, 'drkcfile': 1386}}
    CRDS - INFO - [2014-11-05 13:55:53,001]  Affected products = 670
    CRDS - INFO - [2014-11-05 13:55:53,001]  Unique error types: 0
    CRDS - INFO - [2014-11-05 13:55:53,001]  STARTED 2014-11-05 13:55:10.62
    CRDS - INFO - [2014-11-05 13:55:53,002]  STOPPED 2014-11-05 13:55:53.00
    CRDS - INFO - [2014-11-05 13:55:53,002]  ELAPSED 0:00:42.37
    CRDS - INFO - [2014-11-05 13:55:53,002]  1.43 K datasets at 33.77  datasets-per-second
    CRDS - INFO - [2014-11-05 13:55:53,002]  0 errors
    CRDS - INFO - [2014-11-05 13:55:53,002]  0 warnings
    CRDS - INFO - [2014-11-05 13:55:53,002]  12 infos
    --------------------------------------------------------------------------------------------------------------
    OK: CRDS hst ops datasets affected hst_0295.pmap --> hst_0296.pmap on 2014-11-05-13:55:08 : 670 affected
    --------------------------------------------------------------------------------------------------------------
    ####################################################################################################
    --------------------------------------------------------------------------------------------------------------
    CRDS hst ops datasets affected hst_0296.pmap --> hst_0297.pmap on 2014-11-10-13:15:07
    --------------------------------------------------------------------------------------------------------------
    CRDS - INFO - [2014-11-10 13:15:10,393]  Mapping differences from 'hst_0296.pmap' --> 'hst_0297.pmap' affect:
     {'wfc3': ['darkfile']}
    CRDS - INFO - [2014-11-10 13:15:10,574]  Possibly affected --datasets-since dates determined by 'hst_0296.pmap' --> 'hst_0297.pmap' are:
     {'wfc3': '2014-10-27 00:30:40'}
    CRDS - INFO - [2014-11-10 13:15:10,574]  Computing bestrefs for db datasets for ['wfc3']
    CRDS - INFO - [2014-11-10 13:15:10,574]  Dumping dataset parameters for 'wfc3' from CRDS server at 'https://hst-crds.stsci.edu' since '2014-10-27 00:30:40'
    CRDS - INFO - [2014-11-10 13:15:33,868]  Downloaded  714 dataset ids for 'wfc3' since '2014-10-27 00:30:40'
    CRDS - INFO - [2014-11-10 13:15:43,290]  Updated exposure counts:
     {'WFC3': {'darkfile': 369}}
    CRDS - INFO - [2014-11-10 13:15:43,291]  Affected products = 292
    CRDS - INFO - [2014-11-10 13:15:43,291]  Unique error types: 0
    CRDS - INFO - [2014-11-10 13:15:43,291]  STARTED 2014-11-10 13:15:08.58
    CRDS - INFO - [2014-11-10 13:15:43,291]  STOPPED 2014-11-10 13:15:43.29
    CRDS - INFO - [2014-11-10 13:15:43,291]  ELAPSED 0:00:34.70
    CRDS - INFO - [2014-11-10 13:15:43,291]  714 datasets at 20.57  datasets-per-second
    CRDS - INFO - [2014-11-10 13:15:43,292]  0 errors
    CRDS - INFO - [2014-11-10 13:15:43,292]  0 warnings
    CRDS - INFO - [2014-11-10 13:15:43,292]  12 infos
    --------------------------------------------------------------------------------------------------------------
    OK: CRDS hst ops datasets affected hst_0296.pmap --> hst_0297.pmap on 2014-11-10-13:15:07 : 292 affected
    --------------------------------------------------------------------------------------------------------------
    ####################################################################################################
    CRDS - INFO - Contributing context switches = 2
    CRDS - INFO - Total products affected = 962
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 4 infos

QAD is designed to be run perdiodically,  say every 30 minutes,  to check with the CRDS server for
context updates.  If multiple context switches occur during one polling interval,  by default QAD
includes IDs from all of them.   This is also true of interactive queries using -x and/or -y,  so
it's possible to combine affected datasets from multiple switches when repeated IDs are expected.

QAD also supports a --single-context-switch (-s) mode for printing results 1-by-1 in the advent of
multiple context switches in on polling interval.

Since there is a race condition between when a context is made operational and when affected datasets results
are available on the CRDS server,  QAD also supports a -i switch for ignoring unavailable results.  Alternately
missing results are considered an error,  the main difference being the exit status.

For initialzing,  specify -i to ignore any missing computations since QAD will attempt to process the
entire history the first time it is run and precomputed results don't exist for all historical context
switches.

It's possible for precomputed results to contain bestrefs errors of some sort,  most likely due to invalid
bestrefs selection parametersin the HST DADSOPS catalog.   By default the datasets from a computation which
contained errors are excluded from the overall results.   Use -k to include the dataset IDs from computations
which included errors.

Conversely, to abort processing when an affected datasets computation included errors,  use -z to fail
and quit.

The --quiet (-q) parameter suppresses the recorded log output from the affected datasets computations:

    % query_affected_datasets -x 94 -y 97 -q > ids
    CRDS - INFO - Fetching effects for (94, '2014-11-18 17:15:35', 'hst_0298.pmap', 'Delivery of new ACS DKC, DRK, and BIA files.')
    CRDS - INFO - Fetching effects for (95, '2014-11-20 16:12:34', 'hst_0299.pmap', 'Delivery of new WFC3 UVIS darks.')
    CRDS - INFO - Fetching effects for (96, '2014-11-25 15:48:40', 'hst_0300.pmap', 'Delivery of a new COS HVTAB for association LCIX02080.')
    CRDS - INFO - Contributing context switches = 3
    CRDS - INFO - Total products affected = 10356
    CRDS - INFO - 0 errors
    CRDS - INFO - 0 warnings
    CRDS - INFO - 5 infos

NOTE:  CRDS logging is used in both query_affected_datasets and the original server-side affected datasets computations.  The
final errors count shown above only applies to the client-side computing in query_affected_datasets,  so server-side errors are
not *counted*.   However,  server-side errors are tracked and reduced to a single client-side error for each server-side
bestrefs run with errors.

The --verbose parameter includes debug output in excess of normal application logging,  possibly useful
for debugging subclasses of the QueryAffectedDatasetsScript skeletal framework.

"""
    def add_args(self):
        """Add diff-specific command line parameters."""

        self.add_argument("-l", "--list-history", dest="list_history", action="store_true",
            help="Print out the context history and exit.")

        self.add_argument("-x", "--starting-context", dest="starting_context",
            help="Use the affected datasets computation starting with this history index integer, date, or context name. Defaults to last processed.",
            metavar="INT_OR_NAME", default=None, type=str)

        self.add_argument("-y", "--stopping-context", dest="stopping_context",
            help="Use the affected datasets computation starting with this history index integer, date, or context name. Defaults to end of history.",
            metavar="INT_OR_NAME", default=None, type=str)

        self.add_argument("-s", "--single-context-switch", dest="single_context_switch", action="store_true",
            help="For default indexing, if multiple new contexts are available,  just process one new context and stop.")

        self.add_argument("-i", "--ignore-missing-results", dest="ignore_missing_results", action="store_true",
            help="Skip over any requested context switch which has no pre-computed results on the CRDS server.  Otherwise fatal.")

        self.add_argument("-k", "--ignore-errant-history", dest="ignore_errant_history", action="store_true",
            help="If bestrefs status indicates errors occurred, issue an error message but include the dataset ids in results.")

        self.add_argument("-z", "--fail-on-errant-history", dest="fail_on_errant_history", action="store_true",
            help="If bestrefs status indicates errors occurred, quit processing.  (fix the server and rerun).")

        self.add_argument("-f", "--last-processed-file", dest="last_processed_file",
            help="File containing the tuple of the last history item successfully processed. Defaults to file in CRDS cache.")

        self.add_argument("-q", "--quiet", dest="quiet", action="store_true",
            help="Terser log output.")

        self.add_argument("-r", "--reset", dest="reset", action="store_true",
            help="Reset the last-context-processed file to the end of the current history.  Useful for init and reinit.")

    def __init__(self, *args, **keys):
        super(QueryAffectedDatasetsScript, self).__init__(*args, **keys)
        self.contributing_context_switches = 0

    def main(self):
        """Top level processing method."""
        self.require_server_connection()
        if self.args.list_history:
            return self.list_history()
        if self.args.reset:
            return self.reset_last_processed()
        effects = self.polled()
        ids = self.process(effects)
        self.use_all_ids(effects, ids)
        self.log_all_ids(effects, ids)
        if effects:
            self.save_last_processed(effects)
        return log.errors()

    def process(self,  effects):
        """Output the results of all the context transitions."""
        ids = []
        for i, affected in effects:
            self.log_affected(i, affected)
            if not self.ignore_errors(i, affected):
                ids.extend(affected.affected_ids)
                self.use_affected(i, affected)
                self.contributing_context_switches += 1
        return sorted(set(ids))

    def use_affected(self, i, affected):
        """PLUGIN: for doing something with each individual context switch set of effects. Default does nothing.
        i         -- the ending history index of the transition
        affected  -- dictionary of effects info
        """
        pass

    def use_all_ids(self, effects, ids):
        """PLUGIN: for using all ids which passed availability and error screening. Default prints ids to stdout.

        effects :    [ (history_index, affects info), ...]

        ids :  sorted set of all ids affected by specified or implied contexts
        """
        if ids:
            print("\n".join(ids))

    def log_affected(self, i, affected):
        """PLUGIN: Banner log and debug output for each context switch."""
        if log.get_verbose():
            print("#"*100, file=sys.stderr)
            log.debug("History:", i, "Effects:\n", log.PP(affected))
        else:
            if not self.args.quiet:
                print("#"*100, file=sys.stderr)
                print(affected.bestrefs_err_summary, file=sys.stderr)

    def log_all_ids(self, effects, ids):
        """PLUGIN: Summary output after all contexts processed."""
        if self.args.quiet:
            return
        if not effects:
            log.info("No new results are available.")
        else:
            if not ids:
                log.info("No ids were affected.")
            print("#"*100, file=sys.stderr)
            log.info("Contributing context switches =", len(effects))
            log.info("Total products affected =", len(ids))
        log.standard_status()

    def list_history(self):
        """Print out the context history."""
        for i in range(self.history_start, self.history_stop+1):
            print((i,) + self.history[i])

    @property
    @utils.cached
    def history(self):
        """Return the context history or fail.  Should nominally always work."""
        try:
            return api.get_context_history(self.observatory)
        except Exception as exc:
            self.fatal_error("get_context_history failed: ", str(exc).replace("OtherError:",""))

    def get_affected(self, old_context, new_context):
        """Return the affected datasets Struct for the transition from old_context to new_context,
        or None if the results aren't ready yet.
        """
        try:
            affected = api.get_affected_datasets(self.observatory, old_context, new_context)
        except Exception as exc:
            if "No precomputed affected datasets results exist" in str(exc):
                if self.args.ignore_missing_results:
                    log.info("No results for", old_context, "-->", new_context, "ignoring and proceeding.")
                    affected = None
                else:
                    self.fatal_error("Results for", old_context, "-->", new_context, "don't exist or are not yet complete.")
            else:
                self.fatal_error("get_affected_datasets failed: ", str(exc).replace("OtherError:",""))
        return affected

    def ignore_errors(self, i, affected):
        """Check each context switch for errors during bestrefs run. Fail or return False on errors."""
        ignore = False
        if affected.bestrefs_status != 0:
            message = log.format("CRDS server-side errors for", i, affected.computation_dir)
            if self.args.ignore_errant_history:
                ignore = True
            if self.args.fail_on_errant_history:
                self.fatal_error(message)
            else:
                log.error(message)
        return ignore

    def polled(self):
        """Output the latest affected datasets taken from the history starting item onward.
        Since the history drives and ultimately precedes any affected datasets computation,  there's
        no guarantee that every history item is available.
        """
        assert 0 <= self.history_start < len(self.history), "Invalid history interval with starting index " + repr(self.history_start)
        assert 0 <= self.history_stop  < len(self.history), "Invalid history interval with stopping index " + repr(self.history_stop)
        assert self.history_start <= self.history_stop, "Invalid history interval,  start >= stop."
        effects = []
        for i in range(self.history_start, self.history_stop):
            old_context = self.history[i][1]
            new_context = self.history[i+1][1]
            if old_context > new_context:   # skip over backward transitions,  no output.
                continue
            log.info("Fetching effects for", (i,) + self.history[i+1])
            affected = self.get_affected(old_context, new_context)
            if affected:
                effects.append((i, affected))
        return effects

    @property
    @utils.cached
    def history_start(self):
        """Return the starting item for processing."""
        if self.args.starting_context:
            item = self.convert_context(self.args.starting_context)
        else:  # read the start from the file recording the last successful processing index.
            if os.path.exists(self.last_processed_path) and not self.args.list_history:
                try:
                    last_tuple = utils.evalfile(self.last_processed_path)
                    item = int(last_tuple[0])
                    log.verbose("Loaded last processed:", last_tuple)
                except Exception as exc:
                    self.fatal_error(self.last_processed_path, "already exists but was unusable:", str(exc))
            else:
                item = 0
        return item

    @property
    @utils.cached
    def history_stop(self):
        """Return the stopping item for processing."""
        if self.args.stopping_context:
            item = self.convert_context(self.args.stopping_context)
        else:  # read the start from the file recording the last successful processing index.
            if self.args.single_context_switch:
                item = self.history_start + 1
                if item >= len(self.history) - 1:
                    item = len(self.history) - 1
            else:
                item = len(self.history) - 1
        return item

    def convert_context(self, context):
        """Convert an integer or context name into a history index."""
        try:
            return int(context)
        except ValueError:
            pass
        try:
            date = timestamp.reformat_date(context)
            is_date = True
        except:
            is_date = False
        hist = self.history
        for item, hist in enumerate(hist):
            if is_date and hist[0] >= date:
                break
            elif context in hist[1]:
                break
        else:
            self.fatal_error("Context = '{}' not found in history".format(context))
        assert 0 <= item < len(self.history),  "Invalid history item " + repr(item)
        return item

    def save_last_processed(self, effects):
        """Record the last index history tuple successfully processed."""
        last_ix = effects[-1][0]
        if last_ix == -1:
            return
        hist = (last_ix+1,) + tuple(self.history[last_ix + 1])
        self._write_last_processed(hist)

    def reset_last_processed(self):
        """Reset the state of the last context processed marker to the end of the current history."""
        hist = (len(self.history)-1,) + tuple(self.history[-1])
        self._write_last_processed(hist)

    def _write_last_processed(self, hist):
        """Write down the history tuple of the last context processed."""
        log.verbose("Saving last processed:", repr(hist))
        log.verbose("Storing last processed state at", repr(self.last_processed_path))
        utils.ensure_dir_exists(self.last_processed_path)
        with open(self.last_processed_path, "w+") as last:
            last.write(str(hist))

    @property
    def last_processed_path(self):
        """Path of file recording last processed context."""
        if self.args.last_processed_file:
            return self.args.last_processed_file
        else:
            return os.path.join(config.get_crds_cfgpath(self.observatory), "ad_last_processed")

if __name__ == "__main__":
    sys.exit(QueryAffectedDatasetsScript()())
