import sys
import os
import os.path

from crds import cmdline, log, utils, config
from crds.client import api

class QueryAffectedDatasetsScript(cmdline.Script):

    description = """
Queries the CRDS server for datasets affected by the specified context switch,
defaulting to the latest context switch.  If no server-side bestrefs computation
was performed for the specified context switch, an error occurs;  the server only
has pre-computed results for historical switches.
"""

    def __init__(self, *args, **keys):
        super(QueryAffectedDatasetsScript, self).__init__(*args, **keys)

    def add_args(self):
        """Add diff-specific command line parameters."""

        self.add_argument("-n", "--new-context", dest="new_context", 
            help="Look for affected datasets computation with this new context.",
            metavar="NEW_CONTEXT", default=None, type=cmdline.mapping_spec)
        
        self.add_argument("-o", "--old-context", dest="old_context",
            help="Look for affected datasets computation with this old context.", 
            metavar="OLD_CONTEXT", default=None, type=cmdline.mapping_spec)
        
        self.add_argument("-s", "--since-history-item", dest="since_history_item", 
            help="Output all the affected datasets since the specified history item.  Defaults to save file if unspecified.",
            metavar="HIST_INDEX", default=None, type=int)
        
        self.add_argument("-x", "--since-context", dest="since_context", 
            help="Output affected datasets for all context switches since the last occurrence of context in the history.",
            metavar="CONTEXT_NAME", default=None, type=str)
        
        self.add_argument("-c", "--combine-contexts", dest="combine_contexts",
            help="Merge all affected datasets from all context transitions into a common sorted set.")
        
        self.add_argument("-f", "--since-history-file", dest="since_history_file",
            help="File containing the tuple of the last history item successfully processed.")

        self.add_argument("-p", "--stop-if-not-complete", dest="stop_if_not_complete", action="store_true",
            help="Don't output any datasets if results for any requested history items are not yet available.")

        self.add_argument("-l", "--list-history", dest="list_history", action="store_true",
            help="Print out the context history and exit.")

    def main(self):
        """Top level processing method."""
        
        if self.args.list_history:
            return self.list_history()
        elif self.args.new_context or self.args.old_context:
            effects = self.targeted()
        else:
            effects = self.polled()
            
        if effects:
            self.combine_and_output(effects)
            self.save_last_processed(effects)
        elif effects is not None:
            log.info("No new results available.")
            
        log.standard_status()
        
    def list_history(self):
        """Print out the context history."""
        for i, hist in enumerate(self.history):
            print (i,) + hist
   
    @property
    @utils.cached         
    def history(self):
        """Return the context history or fail.   Should nominally always work."""
        try:
            return tuple(reversed(tuple(tuple(x) for x in api.get_context_history(self.observatory))))
        except Exception as exc:
            self.fatal_error("get_context_history failed: ", str(exc).replace("OtherError:",""))
            
    def get_affected(self, old_context, new_context):
        """Return the affected datasets Struct for the transition from old_context to new_context,  
        or None if the results aren't ready yet.   
        """
        try:
            s = api.get_affected_datasets(self.observatory, old_context, new_context)
        except Exception as exc:
            if "No precomputed affected datasets results exist" in str(exc):
                s = None
            else:
                self.fatal_error("get_affected_datasets failed: ", str(exc).replace("OtherError:",""))
        return s
    
    def combine_and_output(self,  effects):
        """Output the results of all the context transitions."""
        ids = []
        for i, affected in effects:
            log.info("#"*80)
            print >>sys.stderr, affected.bestrefs_err_summary
            ids.extend(affected.affected_ids)
        if self.args.combine_contexts:
            ids = set(ids)
        print "\n".join(ids)
        log.info("#"*80)

    def targeted(self):
        """Output the affected datasets for the specified context(s) interval."""
        s = self.get_affected(self.args.old_context, self.args.new_context)
        print >>sys.stderr, s.bestrefs_err_summary
        print "\n".join(s.affected_ids)
        return [(-1, s)]

    def polled(self):
        """Output the latest affected datasets taken from the history starting item onward.
        Since the history drives and ultimately precedes any affected datasets computation,  there's
        no guarantee that every history item is immediately available.
        """
        old_index = self.history_start
        assert old_index >= 0, "Invalid history interval with starting index " + repr(old_index)
        effects = []
        for i in range(old_index, len(self.history)-1):
            old_context = self.history[i][1]
            new_context = self.history[i+1][1]
            affected = self.get_affected(old_context, new_context)
            if affected is None:
                if self.args.stop_if_not_complete:
                    log.info("Stopping since results for", (old_context, new_context), "are not complete.")
                    return None
                else:
                    log.info("No results for",  (old_context, new_context), "ignoring and proceeding.")
            else:
                effects.append((i, affected))
        return effects

    @property    
    def history_start(self):
        """Return the starting item for polled-mode processing."""
        if self.args.since_history_item:
            item = self.args.since_history_item
        elif self.args.since_context:
            hist = self.history
            for item, hist in enumerate(hist): 
                if self.args.since_context in hist[1]:
                    break
            else:
                self.fatal_error("--since-context='{}' not found in history".format(context))
        else:  # read the start from the file recording the last successful processing index.
            if os.path.exists(self.last_processed_path):
                try:
                    last_tuple = utils.evalfile(self.last_processed_path)
                    item = int(last_tuple[0])
                    log.verbose("Loaded last processed history as", last_tuple)
                except Exception, exc:
                    self.fatal_error(self.last_processed_path, "already exists but was unusable:", str(exc))
            else:
                item = 0
        log.verbose("Determined start of processing as", (item,) + self.history[item])
        return item
        
    def save_last_processed(self, effects):
        """Record the last index history tuple successfully processed."""
        last_ix = effects[-1][0]
        if last_ix == -1:
            return
        hist = (last_ix+1,) + tuple(self.history[last_ix + 1])
        log.verbose("Saving last processed:", repr(hist))
        with open(self.last_processed_path, "w+") as last:
            last.write(str(hist))
                    
    @property
    def last_processed_path(self):
        """Path of file recording last processed context."""
        if self.args.since_history_file:
            return self.args.since_history_file
        else:
            return os.path.join(config.get_crds_cfgpath(self.observatory), "ad_last_processed")
            
if __name__ == "__main__":
    QueryAffectedDatasetsScript()()
