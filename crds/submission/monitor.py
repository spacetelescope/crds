"""This module provides a command line program to monitor a server side
process which communicates via client log messages.
"""

# ===================================================================

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import time

from crds import log, cmdline
from crds.client import api
from crds.log import srepr
from crds import exceptions

# ===================================================================

class MonitorScript(cmdline.Script):
    """Command line script file submission script."""

    description = """
"""

    epilog = """
"""

    def add_args(self):
        """Add class-specifc command line parameters."""
        super(MonitorScript, self).add_args()
        self.add_argument("--submission-key", type=cmdline.process_key,
                          help="Key used to connect to remote process status stream.")
        self.add_argument("--poll-delay", type=int, default=3.0,
                          help="Time in seconds between polling for messages.")

    def main(self):
        """Main control flow of submission directory and request manifest creation."""
        exit_flag = False
        while not exit_flag:
            for message in self._poll_status():
                handler = getattr(self, "handle_" + message.type, self.handle_unknown)
                exit_flag = handler(message)
            time.sleep(self.args.poll_delay)

    def _poll_status(self):
        """Use network API to pull status messages from server."""
        try:
            return api.jpoll_pull_messages(self.args.submission_key)
        except exceptions.StatusChannelNotFoundError:
            log.verbose("Channel", srepr(self.args.submission_key), 
                        "not found.  Waiting for processing to start.")
            return []
        except exceptions.ServiceError as exc:
            log.verbose("Unhandled RPC exception for", srepr(self.args.submission_key), "is", str(exc))
            raise

    def format_remote(self, *params):
        """Format tuple of message `params` in a standardized way for messages 
        coming from the remote process being monitored.
        """
        return log.format("REMOTE:", *params).strip()

    def handle_log_message(self, message):
        """Early API has only one message format,  "log_message".  Issur message info
        and continue monitoring.
        """
        log.info(self.format_remote(message.data))
        return False

    def handle_unknown(self,  message):
        """Handle unknown `message` types by issuing a warning and continuing monitoring."""
        log.warning(self.format_remote("Unknown message type", repr(message.type), "in", repr(message)))
        return False

    def handle_done(self, message):
        """Generic "done" handler issue info() message and stops monitoring / exits."""
        log.info(self.format_remote("Processing complete:", message.data))
        return True

    def handle_cancel(self, message):
        """Generic "cancel" handler reports on commanded cancellation of remote process
        and possibly why it was cancelled.   Then stops monitoring /exits.
        """
        log.warning(self.format_remote("Processing cancelled:", message.data))
        return True

    def handle_fail(self, message):
        """Generic "fail" handler reports on remote process fatal error / failure
        and issues an error() message, then stops monitoring /exits.
        """
        log.error(self.format_remote("Processing failed:",  message.data))
        return True
    
    def handle_error(self, message):
        """Generic "error" handler issues an error message from remote process and
        continues monitoring.
        """
        log.error(self.format_remote(message.data))
        return False
    
    def handle_verbose(self, message):
        """Generic "verbose" handler issues a debug message from remote process if
        this monitor is running verbosely.
        """
        log.verbose(self.format_remote(message.data))
        return False

    def handle_warning(self, message):
        """Generic "warning" handler issues a  warning from remote process and 
        contiues monitoring.
        """
        log.warning(self.format_remote(message.data))
        return False

# ===================================================================

if __name__ == "__main__":
    sys.exit(MonitorScript()())

