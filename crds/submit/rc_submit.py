"""This module adds additional submission metadata and a programmatic interface
to the original commamnd line submission program as part of the file submission
streamlinin project.
"""

import sys

import yaml

from crds.core import log

from .submit import ReferenceSubmissionScript

class RedCatApiScript(ReferenceSubmissionScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """
    def get_submission_args(self):
        """Returns the combined form parameter dictionary as a CRDS Struct defining
        the mapping from all form variables to their string values.
        """
        parameters = super(RedCatApiScript, self).get_submission_args()
        extra_parameters = self.get_extra_parameters()
        parameters.update(extra_parameters)
        return parameters

    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        # ... get and populate required form dictionary,  careful about
        # conflicts with baseclass.   See baseclass self.connection for
        # doing any web i/o.
        
    def batch_submit_references(self):
        """Do a web re-post to the batch submit references web page."""
        return self._submission("/submission_form/redcat_submit/")

class RedCatSubmissionScript(RedCatApiScript):
    """This script extends the original CRDS command line submission
    system with extra meta-data previously captured by the submit_to_redcat
    script.
    """
    def add_args(self):
        super(RedCatSubmissionScript, self).add_args()
        self.add_argument("--redcat-parameters", type=str,
                     help="Path to YAML file defining extra ReDCaT parameters.")
        
    def get_extra_parameters(self):
        """Return the form dictionary mapping form variables to value strings for
        new variables being added by the streamlining project.
        """
        with open(self.args.redcat_parameters) as f:
            text = f.read()
            log.verbose("Raw YAML read:\n", text, verbosity=75)
            loaded = yaml.safe_load(text)
            log.verbose("ReDCaT parameters:\n", log.PP(loaded))
            return loaded

def submit(submission_params, autoconfirm=True, wait=False):
    """Submit reference files and meta information to CRDS

    Parameters
    ----------
    submission_params: dict
        The meta and reference file parameters that define the submission

    autoconfirm: bool
        Complete submission all the way into CRDS.

    wait: bool 
        Wait for the submission to complete before returning.
        On  completion,  successful  submission  will be ready
        for confirmation on web site unless autoconfirm is True.

    Returns
    -------
    monitor: monitor object
        The handle to use to monitor the status of the submission

    """

    # Login to CRDS

    # Certify the reference files
    # In the future this will include checking for duplicate submissions

    # Convert the dict the the appropriate structure.
    # This would involve the use of `add_argument`

    # Post the reference files to the website

    # Post the meta information to the website

    # Return the monitor handle

    script = RedcatApiScript("crds.submit --files {} "
                             "--monitor-processing "
                             "--wait-for-completion "
                             "--wipe-existing-files "
                             "--certify-files "
                             "--log-time "
                             "--stats --creator '{} Team' "
                             "--description '{}'").format(
            submit_files, instrument, description)
    # script._extra_redcat_parameters = {}
    script()


def main():
    """Run the command line program version of the extended batch submit which
    loads extended parameters from a YAML input file.
    """
    script = RedCatSubmissionScript()
    return script()

if __name__ == "__main__":
    sys.exit(main())
