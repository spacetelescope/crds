from __future__ import print_function

import sys
import os
import os.path

from crds import cmdline, log, utils, config
from crds.client import api

class QueryAffectedDatasetsScript(cmdline.Script):

    description = """
query_affected_datasets (QAD) queries the CRDS server for datasets affected by the specified 
context name(s) or indices in the context history.  QAD relies on pre-computed results on the server,
so QAD queries are only valid for historical context transitions from the context history.

Due to processing order on the server, new contexts appear in the context history as operational 
before the datasets affected have been computed.   This framework helps resolve that race condition
and provides options for handling affected datasets computations which contained errors.

With no history range specified, QAD selects the last history item processed as the starting point 
and the end of the current history as the stopping point.  Normally there's nothing new to report,
the last thing processed was the end of the history and nothing has changed on the server.

% query_affected_datasets
CRDS  : INFO     No new results available.
CRDS  : INFO     0 errors
CRDS  : INFO     0 warnings
CRDS  : INFO     1 infos

Polling the the CRDS server by running QAD every 30 minutes, typically QAD will detect context
transitions one-by-one.  If more than one context switch occurs within the same 30 minute period,
QAD will combine the datasets for all transitions into one set.

To support interactive experimentation, QAD supports listing the context history:

% query_affected_datasets --list
(0, '2013-07-02 15:44:53', 'hst.pmap', 'set by system')
(1, '2013-09-10 18:23:06', 'hst_0003.pmap', 'Updated hst.pmap with new references (known to reffile_ops_rep on harpo) up to 09-10-2013')
...
(85, '2014-09-23 16:48:17', 'hst_0287.pmap', 'Delivery of new WFC3 darks.')
(86, '2014-10-13 11:26:40', 'hst_0288.pmap', 'Delivery of a new ACS WFC1-1K bias.')
(87, '2014-10-14 09:34:29', 'hst_0289.pmap', 'Delivery of a new COS FUV BPIXTAB.')

The --quiet parameter suppresses the recorded log output from the affected datasets computations.

The --verbose parameter includes debug output in excess of normal application logging,  possibly useful
for debugging subclasses of the QueryAffectedDatasetsScript skeletal framework.

"""
    def add_args(self):
        """Add diff-specific command line parameters."""

        self.add_argument("-l", "--list-history", dest="list_history", action="store_true",
            help="Print out the context history and exit.")

        self.add_argument("-x", "--starting-context", dest="starting_context",
            help="Use the affected datasets computation starting with this history index integer or context name. Defaults to last processed.", 
            metavar="INT_OR_NAME", default=None, type=str)
        
        self.add_argument("-y", "--stopping-context", dest="stopping_context", 
            help="Use the affected datasets computation starting with this history index integer or context name. Defaults to end of history.",
            metavar="INT_OR_NAME", default=None, type=str)
        
        self.add_argument("-i", "--ignore-missing-results", dest="ignore_missing_results", action="store_true",
            help="Skip over any requested context switch which has no pre-computed results on the CRDS server.  Otherwise fatal.")

        self.add_argument("-k", "--ignore-errant-history", dest="ignore_errant_history", action="store_true",
            help="If bestrefs status indicates errors occurred, issue an error message but include the dataset ids in results.")

        self.add_argument("-z", "--fail-on-errant-history", dest="fail_on_errant_history", action="store_true",
            help="If bestrefs status indicates errors occurred, quit processing.  (fix the server and rerun).")
        
        self.add_argument("-f", "--last-processed-file", dest="last_processed_file",
            help="File containing the tuple of the last history item successfully processed. Defaults to CRDS cache file.")

        self.add_argument("-q", "--quiet", dest="quiet", action="store_true",
            help="Terser log output.")

    def __init__(self, *args, **keys):
        super(QueryAffectedDatasetsScript, self).__init__(*args, **keys)
        self.contributing_context_switches = 0

    def main(self):
        """Top level processing method."""    
        self.require_server_connection()
        if self.args.list_history:
            return self.list_history()
        effects = self.polled()
        if effects:
            self.process(effects)
            self.save_last_processed(effects)
        elif effects is not None:
            log.info("No new results available.")
        log.standard_status()
        
    def process(self,  effects):
        """Output the results of all the context transitions."""
        ids = []
        for i, affected in effects:
            self.log_affected(i, affected)
            if not self.ignore_errors(i, affected):
                ids.extend(affected.affected_ids)
                self.use_affected(i, affected)
                self.contributing_context_switches += 1
        ids = sorted(set(ids))
        self.use_all_ids(effects, ids)
        self.log_total_affected(effects, ids)
        
    def use_affected(self, i, affected):
        """PLUGIN: for doing something with each individual context switch set of effects. Default does nothing."""
        pass
    
    def use_all_ids(self, effects, ids):
        """PLUGIN: for using all ids which passed availability and error screening. Default prints ids to stdout."""
        print("\n".join(ids))
        
    def log_affected(self, i, affected):
        """Banner log and debug output for each context switch."""
        if log.get_verbose():
            print("#"*100, file=sys.stderr)
            log.debug("History:", i, "Effects:\n", log.PP(affected))
        else:
            if not self.args.quiet:
                print("#"*100, file=sys.stderr)
                print(affected.bestrefs_err_summary, file=sys.stderr)

    def log_total_affected(self, effects, ids):
        """Summary output after all contexts processed."""
        if not self.args.quiet:
            print("#"*100, file=sys.stderr)
        log.info("Contributing context switches =", len(effects))
        log.info("Total products affected =", len(ids))
        
    def list_history(self):
        """Print out the context history."""
        for i, hist in enumerate(self.history):
            print((i,) + hist)
   
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

    def targeted(self):
        """Output the affected datasets for the specified context(s) interval."""
        s = self.get_affected(self.args.old_context, self.args.new_context)
        if s:
            print(s.bestrefs_err_summary, file=sys.stderr)
            print("\n".join(s.affected_ids))
            return [(-1, s)]
        else:
            return []

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
            log.info("Fetching effects for", self.history[i+1])
            old_context = self.history[i][1]
            new_context = self.history[i+1][1]
            affected = self.get_affected(old_context, new_context)
            if affected:
                effects.append((i, affected))
        return effects

    @property
    @utils.cached
    def history_start(self):
        """Return the starting item for polled-mode processing."""
        if self.args.starting_context:
            item = self.convert_context(self.args.starting_context)
        else:  # read the start from the file recording the last successful processing index.
            if os.path.exists(self.last_processed_path):
                try:
                    last_tuple = utils.evalfile(self.last_processed_path)
                    item = int(last_tuple[0])
                    log.verbose("Loaded last processed:", last_tuple)
                except Exception, exc:
                    self.fatal_error(self.last_processed_path, "already exists but was unusable:", str(exc))
            else:
                item = 0
        return item
    
    @property
    @utils.cached
    def history_stop(self):
        if self.args.stopping_context:
            item = self.convert_context(self.args.stopping_context)
        else:  # read the start from the file recording the last successful processing index.
            item = len(self.history)-1
        return item
        
    def convert_context(self, context):
        """Convert an integer or context name into a history index."""
        try:
            item = int(context)
        except ValueError:
            hist = self.history
            for item, hist in enumerate(hist): 
                if context in hist[1]:
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
        log.verbose("Saving last processed:", repr(hist))
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
    QueryAffectedDatasetsScript()()
