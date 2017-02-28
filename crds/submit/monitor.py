"""This module provides a command line program to monitor a server side
process which communicates via client log messages.
"""

# ===================================================================

from __future__ import print_function
from __future__ import division
from __future__ import absolute_import

import sys
import time

import numpy as np

from crds.core import exceptions, python23, log, cmdline
from crds.core.log import srepr
from crds.client import api

# ===================================================================

class MonitorScript(cmdline.Script):
    """Command line script to dump real time submission progress messages."""

    description = """Command line script to dump real time submission progress messages.

"""

    epilog = """Monitoring is done with respect to a submission id/key and currently
polls the server for new messages at some periodic rate in seconds:

% python -m crds.monitor --poll-delay 3.0 --key 81323850-9517-416c-ae88-e6481de10a71
"""

    def __init__(self, *args, **keys):
        super(MonitorScript, self).__init__(*args, **keys)
        self._last_id = 0

    def add_args(self):
        """Add class-specifc command line parameters."""
        super(MonitorScript, self).add_args()
        self.add_argument("--key", type=cmdline.process_key,
                          help="Key used to connect to remote process status stream.")
        self.add_argument("--poll-delay", type=int, default=3.0,
                          help="Time in seconds between polling for messages.")

    def main(self):
        """Main control flow of submission directory and request manifest creation."""
        log.divider("monitoring server on " + repr(self.args.key), char="=")
        exit_flag = False
        while not exit_flag:
            for message in self._poll_status():
                handler = getattr(self, "handle_" + message.type, self.handle_unknown)
                exit_flag = handler(message)
            time.sleep(self.args.poll_delay)
        log.divider("monitoring server done", char="=")
        return exit_flag

    def _poll_status(self):
        """Use network API to pull status messages from server."""
        try:
            messages = api.jpoll_pull_messages(self.args.key, since_id=str(self._last_id))
            if messages:
                self._last_id = np.max([int(msg.id) for msg in messages])
            return messages
        except exceptions.StatusChannelNotFoundError:
            log.verbose("Channel", srepr(self.args.key), 
                        "not found.  Waiting for processing to start.")
            return []
        except exceptions.ServiceError as exc:
            log.verbose("Unhandled RPC exception for", srepr(self.args.key), "is", str(exc))
            raise

    def format_remote(self, *params):
        """Format tuple of message `params` in a standardized way for messages 
        coming from the remote process being monitored.
        """
        text = python23.unescape(" ".join(params))
        return log.format(">>", text).strip()

    def handle_log_message(self, message):
        """Early API has only one message format,  "log_message".  Issue message info
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
        status = message.data["status"]
        result = message.data.get("result", None)
        if status == 0:
            log.info(self.format_remote("COMPLETED:", result))
        elif status == 1:
            log.fatal_error(self.format_remote("FAILED:", result))
        elif status == 2:
            log.error(self.format_remote("CANCELLED:", result))
        else:
            log.info(self.format_remote("DONE:", result))
        self.result = result
        return result

    def handle_cancel(self, message):
        """Generic "cancel" handler reports on commanded cancellation of remote process
        and possibly why it was cancelled.   Then stops monitoring /exits.
        """
        log.warning(self.format_remote("Processing cancelled:", message.data))
        return message.data["result"]

    def handle_fail(self, message):
        """Generic "fail" handler reports on remote process fatal error / failure
        and issues an error() message, then stops monitoring /exits.
        """
        log.error(self.format_remote("Processing failed:",  message.data))
        return message.data["result"]
    
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

